"""
Fine-Tuning Framework - Otimiza modelos com dados reais da fazenda

Responsabilidades:
- Transfer learning e fine-tuning
- Estratégias de aprendizado (layer freezing, gradual unfreezing)
- Learning rate scheduling
- Regularização e data augmentation
- Early stopping e model selection
"""

import logging
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau, StepLR, CosineAnnealingLR

from app.training.incremental_trainer import IncrementalTrainer


logger = logging.getLogger(__name__)


@dataclass
class FinetuneConfig:
    """Configuração para fine-tuning"""
    learning_rate: float = 0.0001
    weight_decay: float = 1e-5
    momentum: float = 0.9
    epochs: int = 50
    batch_size: int = 32
    patience: int = 5
    warmup_epochs: int = 2
    freeze_backbone: bool = True
    unfreeze_after_epoch: Optional[int] = None
    lr_scheduler: str = "cosine"  # cosine, step, plateau
    gradient_clip: float = 1.0
    

class FinetuneLearner:
    """
    Framework para fine-tuning de modelos pré-treinados.
    
    Estratégias suportadas:
    - Freezing: Congela backbone, treina apenas head
    - Progressive Unfreezing: Descongela progressivamente
    - Discriminative Learning Rates: Taxa de aprendizado por camada
    - Layer-wise Learning Rate Decay: Decay diferente por camada
    
    Exemplo:
        ```python
        learner = FinetuneLearner(model, trainer, device="cuda")
        
        # Fine-tune com estratégia padrão
        await learner.finetune_and_evaluate(
            train_loader=train_loader,
            val_loader=val_loader,
            config=FinetuneConfig(
                learning_rate=0.0001,
                epochs=50,
                freeze_backbone=True,
            ),
        )
        
        # Visualizar resultados
        results = learner.get_results()
        print(results["summary"])
        ```
    """
    
    def __init__(
        self,
        model: nn.Module,
        trainer: IncrementalTrainer,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        """
        Inicializa o learner para fine-tuning.
        
        Args:
            model: Modelo PyTorch a fine-tunar
            trainer: IncrementalTrainer para gerenciar dados/checkpoints
            device: Dispositivo (cuda/cpu)
        """
        self.model = model
        self.trainer = trainer
        self.device = device
        
        self.results: Dict = {
            "config": None,
            "train_losses": [],
            "val_losses": [],
            "val_accuracies": [],
            "learning_rates": [],
            "best_epoch": None,
            "best_val_loss": float("inf"),
            "best_val_accuracy": 0.0,
            "summary": {},
        }
        
        self.optimizer: Optional[optim.Optimizer] = None
        self.scheduler: Optional[object] = None
        self.loss_fn: Optional[nn.Module] = None
    
    def _freeze_backbone(self):
        """Congela os pesos do backbone."""
        for name, param in self.model.named_parameters():
            if "backbone" in name or "features" in name:
                param.requires_grad = False
                logger.info(f"Frozen: {name}")
    
    def _unfreeze_all(self):
        """Descongela todos os pesos."""
        for param in self.model.parameters():
            param.requires_grad = True
        logger.info("Unfrozen all parameters")
    
    def _unfreeze_layer(self, layer_name: str):
        """Descongela uma camada específica."""
        for name, param in self.model.named_parameters():
            if layer_name in name:
                param.requires_grad = True
        logger.info(f"Unfrozen: {layer_name}")
    
    def get_discriminative_lr_groups(self, base_lr: float) -> List[Dict]:
        """
        Obtém grupos de parâmetros com learning rates discriminativas.
        
        Taxa de aprendizado varia por profundidade da camada.
        
        Args:
            base_lr: Learning rate base
            
        Returns:
            Lista de grupos de parâmetros com LRs diferentes
        """
        groups = []
        
        # Backbone com taxa mais baixa
        backbone_params = []
        head_params = []
        
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                if "backbone" in name or "features" in name:
                    backbone_params.append(param)
                else:
                    head_params.append(param)
        
        if backbone_params:
            groups.append({"params": backbone_params, "lr": base_lr * 0.1})
        
        if head_params:
            groups.append({"params": head_params, "lr": base_lr})
        
        return groups if groups else [{"params": self.model.parameters(), "lr": base_lr}]
    
    def setup_optimizer(
        self,
        config: FinetuneConfig,
        optimizer_type: str = "adamw",
    ):
        """
        Configura otimizador com estratégia apropriada.
        
        Args:
            config: Configuração de fine-tuning
            optimizer_type: Tipo de otimizador (adamw, sgd, adam)
        """
        # Freeze backbone se configurado
        if config.freeze_backbone:
            self._freeze_backbone()
        
        # Obter grupos de parâmetros
        param_groups = self.get_discriminative_lr_groups(config.learning_rate)
        
        # Criar otimizador
        if optimizer_type == "adamw":
            self.optimizer = optim.AdamW(
                param_groups,
                weight_decay=config.weight_decay,
            )
        elif optimizer_type == "sgd":
            self.optimizer = optim.SGD(
                param_groups,
                momentum=config.momentum,
                weight_decay=config.weight_decay,
            )
        else:
            self.optimizer = optim.Adam(param_groups)
        
        logger.info(f"Configured {optimizer_type} optimizer")
        
        # Configurar scheduler
        self._setup_scheduler(config)
    
    def _setup_scheduler(self, config: FinetuneConfig):
        """Configura learning rate scheduler."""
        if config.lr_scheduler == "cosine":
            self.scheduler = CosineAnnealingLR(
                self.optimizer,
                T_max=config.epochs,
                eta_min=1e-6,
            )
        elif config.lr_scheduler == "step":
            self.scheduler = StepLR(
                self.optimizer,
                step_size=config.epochs // 3,
                gamma=0.1,
            )
        elif config.lr_scheduler == "plateau":
            self.scheduler = ReduceLROnPlateau(
                self.optimizer,
                mode="min",
                factor=0.5,
                patience=2,
                verbose=True,
            )
        
        logger.info(f"Configured {config.lr_scheduler} scheduler")
    
    async def finetune_and_evaluate(
        self,
        train_loader,
        val_loader,
        config: FinetuneConfig,
        loss_fn: Optional[nn.Module] = None,
        train_step_fn: Optional[Callable] = None,
        val_step_fn: Optional[Callable] = None,
    ) -> Dict:
        """
        Executa fine-tuning completo com avaliação.
        
        Args:
            train_loader: DataLoader de treinamento
            val_loader: DataLoader de validação
            config: Configuração de fine-tuning
            loss_fn: Função de loss (usa CrossEntropyLoss por padrão)
            train_step_fn: Função customizada de treinamento (opcional)
            val_step_fn: Função customizada de validação (opcional)
            
        Returns:
            Dict com resultados do fine-tuning
        """
        logger.info("Starting fine-tuning...")
        
        self.results["config"] = config.__dict__
        self.loss_fn = loss_fn or nn.CrossEntropyLoss()
        
        # Setup otimizador
        self.setup_optimizer(config)
        
        # Training loop
        for epoch in range(config.epochs):
            # Progressive unfreezing
            if config.unfreeze_after_epoch and epoch == config.unfreeze_after_epoch:
                self._unfreeze_all()
            
            # Warmup learning rate
            if epoch < config.warmup_epochs:
                for param_group in self.optimizer.param_groups:
                    param_group["lr"] *= (epoch + 1) / config.warmup_epochs
            
            # Train
            train_loss = await self._train_epoch(
                train_loader,
                train_step_fn,
                config.gradient_clip,
            )
            
            # Validate
            val_loss, val_accuracy = await self._validate_epoch(val_loader, val_step_fn)
            
            # Record
            self.results["train_losses"].append(train_loss)
            self.results["val_losses"].append(val_loss)
            self.results["val_accuracies"].append(val_accuracy)
            
            current_lr = self.optimizer.param_groups[0]["lr"]
            self.results["learning_rates"].append(current_lr)
            
            logger.info(
                f"Epoch {epoch+1}/{config.epochs}: "
                f"Train Loss={train_loss:.4f}, Val Loss={val_loss:.4f}, "
                f"Val Acc={val_accuracy:.4f}, LR={current_lr:.6f}"
            )
            
            # Step scheduler
            if isinstance(self.scheduler, ReduceLROnPlateau):
                self.scheduler.step(val_loss)
            else:
                self.scheduler.step()
            
            # Track best model
            if val_loss < self.results["best_val_loss"]:
                self.results["best_val_loss"] = val_loss
                self.results["best_val_accuracy"] = val_accuracy
                self.results["best_epoch"] = epoch
                
                # Save best model
                self.trainer.save_checkpoint(
                    self.model,
                    epoch,
                    train_loss,
                    val_loss,
                    val_accuracy,
                    self.optimizer,
                )
                logger.info(f"Best model saved at epoch {epoch}")
            
            # Early stopping
            if epoch - self.results["best_epoch"] > config.patience:
                logger.info(f"Early stopping at epoch {epoch}")
                break
        
        # Gerar sumário
        self._generate_summary()
        
        return self.results
    
    async def _train_epoch(
        self,
        train_loader,
        train_step_fn: Optional[Callable],
        gradient_clip: float,
    ) -> float:
        """Treina uma época."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch_idx, batch in enumerate(train_loader):
            self.optimizer.zero_grad()
            
            if train_step_fn:
                loss = await train_step_fn(self.model, batch, self.device, self.loss_fn)
            else:
                x, y = batch
                x = x.to(self.device)
                y = y.to(self.device)
                
                outputs = self.model(x)
                loss = self.loss_fn(outputs, y)
            
            loss.backward()
            
            # Gradient clipping
            if gradient_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), gradient_clip)
            
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        return total_loss / num_batches if num_batches > 0 else 0.0
    
    async def _validate_epoch(
        self,
        val_loader,
        val_step_fn: Optional[Callable],
    ) -> Tuple[float, float]:
        """Valida uma época."""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        num_batches = 0
        
        with torch.no_grad():
            for batch in val_loader:
                if val_step_fn:
                    loss, acc = await val_step_fn(self.model, batch, self.device, self.loss_fn)
                    total_loss += loss
                    correct += acc
                    total += 1
                else:
                    x, y = batch
                    x = x.to(self.device)
                    y = y.to(self.device)
                    
                    outputs = self.model(x)
                    loss = self.loss_fn(outputs, y)
                    
                    total_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    correct += (predicted == y).sum().item()
                    total += y.size(0)
                
                num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        accuracy = correct / total if total > 0 else 0.0
        
        return avg_loss, accuracy
    
    def _generate_summary(self):
        """Gera sumário de resultados."""
        self.results["summary"] = {
            "total_epochs_trained": len(self.results["train_losses"]),
            "best_epoch": self.results["best_epoch"],
            "best_val_loss": self.results["best_val_loss"],
            "best_val_accuracy": self.results["best_val_accuracy"],
            "final_val_accuracy": self.results["val_accuracies"][-1] if self.results["val_accuracies"] else 0.0,
            "improvement": self.results["val_accuracies"][-1] - self.results["val_accuracies"][0] if len(self.results["val_accuracies"]) > 1 else 0.0,
            "average_val_accuracy": sum(self.results["val_accuracies"]) / len(self.results["val_accuracies"]) if self.results["val_accuracies"] else 0.0,
        }
    
    def get_results(self) -> Dict:
        """Retorna resultados de fine-tuning."""
        return self.results
    
    def export_results(self, filepath: str):
        """Exporta resultados para arquivo JSON."""
        try:
            with open(filepath, "w") as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Exported results to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
    
    def plot_training_history(self) -> Dict:
        """Retorna dados para plotagem de histórico."""
        return {
            "train_losses": self.results["train_losses"],
            "val_losses": self.results["val_losses"],
            "val_accuracies": self.results["val_accuracies"],
            "learning_rates": self.results["learning_rates"],
        }
