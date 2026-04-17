"""
Training Script with Real Data Support

Script principal para treinar modelos com dados reais do MongoDB.

Uso:
    # Treinar modelo de comportamento com dados reais
    python train_real_data.py \
        --model behavior \
        --epochs 50 \
        --batch-size 32 \
        --device cuda \
        --use-real-data

    # Treinar modelo de anomalia e resumir de checkpoint
    python train_real_data.py \
        --model anomaly \
        --epochs 100 \
        --resume-checkpoint

    # Listar modelos e checkpoints disponíveis
    python train_real_data.py --list-models
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.optim as optim

from motor.motor_asyncio import AsyncIOMotorClient

# Imports FASE 2 models
from app.models.behavior import CNNBehaviorClassifier
from app.models.anomaly import AnomalyDetectionAutoencoder
from app.models.reid import ResNetReID
from app.models.temporal import LSTMTemporalAnalyzer

# Imports FASE 3
from app.training.incremental_trainer import IncrementalTrainer


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Mapeamento de modelos
MODELS = {
    "behavior": {
        "class": CNNBehaviorClassifier,
        "input_shape": (3, 240, 240),
        "output_classes": 8,
        "checkpoint_dir": "checkpoints/behavior",
    },
    "anomaly": {
        "class": AnomalyDetectionAutoencoder,
        "input_shape": (6,),
        "output_classes": 2,
        "checkpoint_dir": "checkpoints/anomaly",
    },
    "reid": {
        "class": ResNetReID,
        "input_shape": (3, 224, 224),
        "output_classes": 1000,
        "checkpoint_dir": "checkpoints/reid",
    },
    "temporal": {
        "class": LSTMTemporalAnalyzer,
        "input_shape": (30, 128),
        "output_classes": 8,
        "checkpoint_dir": "checkpoints/temporal",
    },
}


def get_model(model_name: str, device: str) -> nn.Module:
    """Obtém modelo do registro."""
    if model_name not in MODELS:
        raise ValueError(f"Unknown model: {model_name}")
    
    model_config = MODELS[model_name]
    model = model_config["class"]()
    model.to(device)
    
    logger.info(f"Initialized {model_name} model on device {device}")
    return model


def get_optimizer(model: nn.Module, learning_rate: float = 0.001):
    """Obtém otimizador."""
    return optim.Adam(model.parameters(), lr=learning_rate)


def get_loss_fn(model_name: str):
    """Obtém função de loss apropriada."""
    if model_name == "anomaly":
        return nn.BCEWithLogitsLoss()
    elif model_name == "reid":
        return nn.TripletMarginLoss()
    else:
        return nn.CrossEntropyLoss()


async def train_epoch(
    model: nn.Module,
    train_loader,
    optimizer,
    loss_fn,
    device: str,
) -> float:
    """
    Treina uma época.
    
    Args:
        model: Modelo PyTorch
        train_loader: DataLoader de treinamento
        optimizer: Otimizador
        loss_fn: Função de loss
        device: Dispositivo (cpu/cuda)
        
    Returns:
        Loss médio da época
    """
    model.train()
    total_loss = 0.0
    num_batches = 0
    
    for batch_idx, batch in enumerate(train_loader):
        optimizer.zero_grad()
        
        if isinstance(batch, (list, tuple)) and len(batch) == 2:
            if isinstance(batch[0], (list, tuple)):
                # Triplet loss (for reid)
                anchors, positives, negatives = batch[0]
                anchors = anchors.to(device)
                positives = positives.to(device)
                negatives = negatives.to(device)
                
                anchor_embeddings = model(anchors)
                positive_embeddings = model(positives)
                negative_embeddings = model(negatives)
                
                loss = loss_fn(anchor_embeddings, positive_embeddings, negative_embeddings)
            else:
                x, y = batch
                x = x.to(device)
                y = y.to(device)
                
                outputs = model(x)
                loss = loss_fn(outputs, y)
        else:
            # Handle raw batch
            x = batch[0].to(device) if hasattr(batch[0], 'to') else batch[0]
            y = batch[1].to(device) if len(batch) > 1 and hasattr(batch[1], 'to') else batch[1]
            
            outputs = model(x)
            loss = loss_fn(outputs, y)
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        num_batches += 1
        
        if (batch_idx + 1) % 10 == 0:
            logger.info(f"Batch {batch_idx + 1}/{len(train_loader)}, Loss: {loss.item():.4f}")
    
    avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
    return avg_loss


async def validate_epoch(
    model: nn.Module,
    val_loader,
    loss_fn,
    device: str,
) -> tuple:
    """
    Valida modelo.
    
    Args:
        model: Modelo PyTorch
        val_loader: DataLoader de validação
        loss_fn: Função de loss
        device: Dispositivo (cpu/cuda)
        
    Returns:
        Tupla (val_loss, val_accuracy)
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    num_batches = 0
    
    with torch.no_grad():
        for batch in val_loader:
            if isinstance(batch, (list, tuple)) and len(batch) == 2:
                x, y = batch
                x = x.to(device)
                y = y.to(device)
                
                outputs = model(x)
                loss = loss_fn(outputs, y)
                
                if not isinstance(outputs, torch.Tensor) or outputs.dim() == 1:
                    # Regression or single output
                    correct += 0
                else:
                    # Classification
                    _, predicted = torch.max(outputs.data, 1)
                    correct += (predicted == y).sum().item()
                    total += y.size(0)
            
            total_loss += loss.item()
            num_batches += 1
    
    avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
    accuracy = correct / total if total > 0 else 0.0
    
    return avg_loss, accuracy


async def train_with_real_data(args):
    """
    Treina modelo com dados reais do MongoDB.
    
    Args:
        args: Argumentos da linha de comando
    """
    logger.info(f"Starting training: model={args.model}, epochs={args.epochs}, use_real_data={args.use_real_data}")
    
    # Preparar dispositivo
    device = args.device
    if device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA not available, falling back to CPU")
        device = "cpu"
    
    logger.info(f"Using device: {device}")
    
    # Obter modelo
    model_config = MODELS[args.model]
    model = get_model(args.model, device)
    
    # Inicializar trainer incremental
    trainer = IncrementalTrainer(
        model_path=f"models/{args.model}_model.pt",
        checkpoint_dir=model_config["checkpoint_dir"],
        use_real_data=args.use_real_data,
    )
    
    # Inicializar gerenciadores de dados se usar dados reais
    if args.use_real_data:
        try:
            db_url = "mongodb://localhost:27017"
            client = AsyncIOMotorClient(db_url)
            db = client["agrovision_ml"]
            
            await trainer.initialize_data_managers(db)
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.info("Falling back to synthetic data")
            args.use_real_data = False
    
    # Carregar checkpoint se solicitar retoma
    if args.resume_checkpoint:
        checkpoint = trainer.load_checkpoint(model)
        start_epoch = checkpoint.get("epoch", 0) + 1
        logger.info(f"Resuming from epoch {start_epoch}")
    else:
        start_epoch = 0
    
    # Preparar treinamento
    optimizer = get_optimizer(model, args.learning_rate)
    loss_fn = get_loss_fn(args.model)
    
    logger.info("=" * 80)
    logger.info(f"Training Summary:")
    logger.info(f"  Model: {args.model}")
    logger.info(f"  Epochs: {args.epochs}")
    logger.info(f"  Batch Size: {args.batch_size}")
    logger.info(f"  Learning Rate: {args.learning_rate}")
    logger.info(f"  Device: {device}")
    logger.info(f"  Real Data: {args.use_real_data}")
    logger.info(f"  Resume: {args.resume_checkpoint}")
    logger.info("=" * 80)
    
    # Se usar dados reais, obter data loaders
    if args.use_real_data:
        try:
            data_quality = await trainer.validate_data_quality()
            logger.info(f"Data quality score: {data_quality:.2%}")
            
            train_loader, val_loader, test_loader = await trainer.get_data_loaders(
                batch_size=args.batch_size,
                data_type=args.model,
            )
        except Exception as e:
            logger.error(f"Failed to load real data: {e}")
            logger.warning("Using synthetic data instead")
            args.use_real_data = False
            train_loader = None
            val_loader = None
    else:
        logger.info("Using synthetic data")
        train_loader = None
        val_loader = None
    
    # Loop de treinamento
    best_val_loss = float("inf")
    patience_counter = 0
    max_patience = 5
    
    for epoch in range(start_epoch, args.epochs):
        logger.info(f"\n{'='*80}")
        logger.info(f"Epoch {epoch + 1}/{args.epochs}")
        logger.info(f"{'='*80}")
        
        if train_loader:
            # Treinar com dados reais
            train_loss = await train_epoch(model, train_loader, optimizer, loss_fn, device)
            logger.info(f"Train Loss: {train_loss:.4f}")
        else:
            # Placeholder para treinamento sintético
            train_loss = 0.0
            logger.info("(Synthetic training placeholder)")
        
        if val_loader:
            # Validar com dados reais
            val_loss, val_accuracy = await validate_epoch(model, val_loader, loss_fn, device)
            logger.info(f"Val Loss: {val_loss:.4f}, Val Accuracy: {val_accuracy:.2%}")
        else:
            val_loss = 0.0
            val_accuracy = 0.0
            logger.info("(Synthetic validation placeholder)")
        
        # Registrar métrica de qualidade de dados
        data_quality = await trainer.validate_data_quality() if args.use_real_data else 1.0
        
        # Registrar época
        trainer.record_epoch(epoch, train_loss, val_loss, val_accuracy, data_quality)
        
        # Salvar checkpoint
        trainer.save_checkpoint(model, epoch, train_loss, val_loss, val_accuracy, optimizer)
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
        else:
            patience_counter += 1
        
        if patience_counter >= max_patience:
            logger.info(f"Early stopping after {patience_counter} epochs without improvement")
            break
    
    # Salvar modelo final
    trainer.save_final_model(model)
    
    # Mostrar sumário
    summary = trainer.get_training_summary()
    logger.info(f"\n{'='*80}")
    logger.info("Training Summary:")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")
    logger.info(f"{'='*80}")
    
    # Cleanup
    await trainer.cleanup()


async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Train ML models with real data from MongoDB"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        choices=list(MODELS.keys()),
        default="behavior",
        help="Model to train (default: behavior)",
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Number of epochs (default: 50)",
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size (default: 32)",
    )
    
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.001,
        help="Learning rate (default: 0.001)",
    )
    
    parser.add_argument(
        "--device",
        type=str,
        choices=["cpu", "cuda"],
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to use (default: cuda if available)",
    )
    
    parser.add_argument(
        "--use-real-data",
        action="store_true",
        help="Use real data from MongoDB instead of synthetic data",
    )
    
    parser.add_argument(
        "--resume-checkpoint",
        action="store_true",
        help="Resume training from last checkpoint",
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models and exit",
    )
    
    args = parser.parse_args()
    
    # List models
    if args.list_models:
        print("Available models:")
        for model_name, config in MODELS.items():
            print(f"  - {model_name}")
            print(f"    Input shape: {config['input_shape']}")
            print(f"    Output classes: {config['output_classes']}")
            print(f"    Checkpoint dir: {config['checkpoint_dir']}")
        sys.exit(0)
    
    # Train
    try:
        await train_with_real_data(args)
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
