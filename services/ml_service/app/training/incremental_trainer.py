"""
Incremental Trainer - Treinamento contínuo com dados reais do MongoDB

Responsabilidades:
- Treinamento incremental resumindo de checkpoints
- Integração com dados reais via RealDataTrainingManager
- Rastreamento de progresso de treinamento
- Validação contínua de dados
- Suporte para múltiplos modelos
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import json

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from app.data.training_manager import RealDataTrainingManager
from app.data.data_sync import IncrementalDataManager


logger = logging.getLogger(__name__)


class IncrementalTrainer:
    """
    Treinador incremental que suporta:
    - Retomada de checkpoints anteriores
    - Treinamento com dados reais do MongoDB
    - Rastreamento de progresso persistente
    - Validação de qualidade de dados
    
    Exemplo:
        ```python
        trainer = IncrementalTrainer(
            model_path="models/behavior_classifier.pt",
            checkpoint_dir="checkpoints/",
        )
        
        # Primeira vez: treina do zero
        await trainer.train(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            epochs=50,
            use_real_data=True,
        )
        
        # Próxima vez: retoma do último checkpoint
        await trainer.train(...)
        ```
    """
    
    def __init__(
        self,
        model_path: str,
        checkpoint_dir: str = "checkpoints",
        use_real_data: bool = False,
    ):
        """
        Inicializa o treinador incremental.
        
        Args:
            model_path: Caminho para salvar o modelo
            checkpoint_dir: Diretório para checkpoints
            use_real_data: Usar dados reais do MongoDB
        """
        self.model_path = Path(model_path)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.use_real_data = use_real_data
        
        self.checkpoint_dir.mkdir(exist_ok=True, parents=True)
        self.model_path.parent.mkdir(exist_ok=True, parents=True)
        
        self.training_history: Dict = {
            "epochs": [],
            "train_loss": [],
            "val_loss": [],
            "val_accuracy": [],
            "data_quality": [],
            "timestamps": [],
        }
        
        self.history_file = self.checkpoint_dir / "training_history.json"
        self._load_history()
        
        self.data_manager: Optional[IncrementalDataManager] = None
        self.training_manager: Optional[RealDataTrainingManager] = None
    
    async def initialize_data_managers(self, db):
        """
        Inicializa gerenciadores de dados.
        
        Args:
            db: Motor AsyncIOMotorDatabase
        """
        if self.use_real_data:
            self.training_manager = RealDataTrainingManager()
            await self.training_manager.connect()
            
            self.data_manager = IncrementalDataManager(db)
            await self.data_manager.initialize()
            
            logger.info("Initialized data managers for real data training")
    
    def _load_history(self):
        """Carrega histórico de treinamento anterior."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    self.training_history = json.load(f)
                logger.info(f"Loaded training history with {len(self.training_history['epochs'])} epochs")
            except Exception as e:
                logger.warning(f"Could not load training history: {e}")
                self.training_history = {
                    "epochs": [],
                    "train_loss": [],
                    "val_loss": [],
                    "val_accuracy": [],
                    "data_quality": [],
                    "timestamps": [],
                }
    
    def _save_history(self):
        """Salva histórico de treinamento."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.training_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save training history: {e}")
    
    def get_start_epoch(self) -> int:
        """Obtém a época inicial (retoma do último checkpoint)."""
        if self.training_history["epochs"]:
            return max(self.training_history["epochs"]) + 1
        return 0
    
    async def get_data_loaders(
        self,
        batch_size: int = 32,
        data_type: str = "behavior",
    ) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Obtém data loaders para treinamento.
        
        Args:
            batch_size: Tamanho do batch
            data_type: Tipo de dados (behavior, anomaly, reid, temporal)
            
        Returns:
            Tupla (train_loader, val_loader, test_loader)
        """
        if not self.use_real_data:
            raise ValueError("Must initialize with use_real_data=True")
        
        if not self.training_manager:
            raise RuntimeError("Data manager not initialized. Call initialize_data_managers()")
        
        logger.info(f"Loading {data_type} datasets from MongoDB...")
        
        if data_type == "behavior":
            train_ds, val_ds, test_ds = await self.training_manager.get_behavior_dataset()
        elif data_type == "anomaly":
            train_ds, val_ds, test_ds = await self.training_manager.get_anomaly_dataset()
        elif data_type == "reid":
            train_ds, val_ds, test_ds = await self.training_manager.get_reid_dataset()
        elif data_type == "temporal":
            train_ds, val_ds, test_ds = await self.training_manager.get_temporal_dataset()
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=2)
        val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=2)
        test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=2)
        
        logger.info(f"Loaded data: train={len(train_ds)}, val={len(val_ds)}, test={len(test_ds)}")
        
        return train_loader, val_loader, test_loader
    
    def get_checkpoint_path(self, epoch: int) -> Path:
        """Retorna caminho do checkpoint para uma época."""
        return self.checkpoint_dir / f"checkpoint_epoch_{epoch:04d}.pt"
    
    def load_checkpoint(self, model: nn.Module, epoch: Optional[int] = None) -> Dict:
        """
        Carrega checkpoint anterior.
        
        Args:
            model: Modelo PyTorch
            epoch: Época específica (None = última)
            
        Returns:
            Dict com estado do checkpoint
        """
        if epoch is None:
            # Encontrar último checkpoint
            checkpoints = sorted(self.checkpoint_dir.glob("checkpoint_epoch_*.pt"))
            if not checkpoints:
                logger.info("No checkpoints found, starting from scratch")
                return {"epoch": 0, "model_state": None}
            checkpoint_path = checkpoints[-1]
        else:
            checkpoint_path = self.get_checkpoint_path(epoch)
        
        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint not found: {checkpoint_path}")
            return {"epoch": 0, "model_state": None}
        
        try:
            checkpoint = torch.load(checkpoint_path, map_location="cpu")
            model.load_state_dict(checkpoint["model_state"])
            logger.info(f"Loaded checkpoint from epoch {checkpoint['epoch']}")
            return checkpoint
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return {"epoch": 0, "model_state": None}
    
    def save_checkpoint(
        self,
        model: nn.Module,
        epoch: int,
        train_loss: float,
        val_loss: float,
        val_accuracy: float,
        optimizer=None,
    ):
        """
        Salva checkpoint do modelo.
        
        Args:
            model: Modelo PyTorch
            epoch: Número da época
            train_loss: Loss de treinamento
            val_loss: Loss de validação
            val_accuracy: Acurácia de validação
            optimizer: Otimizador (opcional)
        """
        checkpoint = {
            "epoch": epoch,
            "model_state": model.state_dict(),
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_accuracy": val_accuracy,
            "timestamp": datetime.now().isoformat(),
        }
        
        if optimizer:
            checkpoint["optimizer_state"] = optimizer.state_dict()
        
        checkpoint_path = self.get_checkpoint_path(epoch)
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Saved checkpoint to {checkpoint_path}")
    
    def save_final_model(self, model: nn.Module):
        """Salva modelo final."""
        torch.save(model.state_dict(), self.model_path)
        logger.info(f"Saved final model to {self.model_path}")
    
    def record_epoch(
        self,
        epoch: int,
        train_loss: float,
        val_loss: float,
        val_accuracy: float,
        data_quality: Optional[float] = None,
    ):
        """
        Registra métricas de uma época.
        
        Args:
            epoch: Número da época
            train_loss: Loss de treinamento
            val_loss: Loss de validação
            val_accuracy: Acurácia de validação
            data_quality: Score de qualidade de dados (0-1)
        """
        self.training_history["epochs"].append(epoch)
        self.training_history["train_loss"].append(train_loss)
        self.training_history["val_loss"].append(val_loss)
        self.training_history["val_accuracy"].append(val_accuracy)
        self.training_history["data_quality"].append(data_quality or 1.0)
        self.training_history["timestamps"].append(datetime.now().isoformat())
        
        self._save_history()
    
    async def validate_data_quality(self) -> float:
        """
        Valida qualidade dos dados de treinamento.
        
        Returns:
            Score de qualidade (0-1)
        """
        if not self.training_manager:
            return 1.0
        
        try:
            quality = await self.training_manager.validate_data_quality()
            
            total_valid = sum(
                v for k, v in quality.get("valid", {}).items()
                if isinstance(v, int)
            )
            total_invalid = sum(
                v for k, v in quality.get("invalid", {}).items()
                if isinstance(v, int)
            )
            
            total = total_valid + total_invalid
            quality_score = total_valid / total if total > 0 else 1.0
            
            logger.info(f"Data quality score: {quality_score:.2%}")
            return quality_score
        except Exception as e:
            logger.error(f"Failed to validate data quality: {e}")
            return 1.0
    
    def get_training_summary(self) -> Dict:
        """Retorna sumário do treinamento até agora."""
        if not self.training_history["epochs"]:
            return {
                "total_epochs": 0,
                "current_status": "not_started",
            }
        
        epochs = self.training_history["epochs"]
        return {
            "total_epochs": len(epochs),
            "current_status": "in_progress" if max(epochs) > 0 else "starting",
            "last_epoch": max(epochs),
            "best_val_loss": min(self.training_history["val_loss"]),
            "best_val_accuracy": max(self.training_history["val_accuracy"]),
            "average_val_accuracy": sum(self.training_history["val_accuracy"]) / len(self.training_history["val_accuracy"]),
            "training_time_hours": len(epochs) * 0.5,  # Aproximado
            "use_real_data": self.use_real_data,
        }
    
    async def cleanup(self):
        """Limpa recursos."""
        if self.training_manager:
            await self.training_manager.disconnect()
        logger.info("Incremental trainer cleanup complete")
