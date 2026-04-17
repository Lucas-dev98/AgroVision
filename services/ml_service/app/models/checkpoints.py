"""Model checkpoint management for persistence and resumable training"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

import torch
import torch.nn as nn
from torch.optim.optimizer import Optimizer


class ModelCheckpoint:
    """Manage model checkpoints for training and inference"""

    def __init__(self, checkpoint_dir: str = "models_data"):
        """
        Initialize checkpoint manager
        
        Args:
            checkpoint_dir: Directory to store checkpoints
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        model: nn.Module,
        optimizer: Optional[Optimizer],
        epoch: int,
        metrics: Dict[str, float],
        checkpoint_name: str,
        **kwargs,
    ) -> str:
        """
        Save full training checkpoint
        
        Args:
            model: PyTorch model
            optimizer: Optimizer instance
            epoch: Current epoch
            metrics: Training metrics dict
            checkpoint_name: Checkpoint name (e.g., "behavior_classifier")
            **kwargs: Additional metadata
            
        Returns:
            Path to checkpoint file
        """
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_name}_epoch{epoch}.pt"
        
        checkpoint_data = {
            "epoch": epoch,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict() if optimizer else None,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
            **kwargs,
        }
        
        torch.save(checkpoint_data, checkpoint_path)
        print(f"✅ Checkpoint saved: {checkpoint_path}")
        
        return str(checkpoint_path)

    def load_checkpoint(
        self,
        model: nn.Module,
        checkpoint_path: str,
        optimizer: Optional[Optimizer] = None,
        device: str = "cpu",
    ) -> Tuple[nn.Module, Optional[Optimizer], int, Dict[str, float]]:
        """
        Load full training checkpoint and resume
        
        Args:
            model: PyTorch model
            checkpoint_path: Path to checkpoint
            optimizer: Optimizer instance
            device: Device to load on
            
        Returns:
            (model, optimizer, epoch, metrics)
        """
        checkpoint_data = torch.load(checkpoint_path, map_location=device)
        
        model.load_state_dict(checkpoint_data["model_state"])
        
        if optimizer and checkpoint_data["optimizer_state"]:
            optimizer.load_state_dict(checkpoint_data["optimizer_state"])
        
        epoch = checkpoint_data["epoch"]
        metrics = checkpoint_data["metrics"]
        
        print(f"✅ Checkpoint loaded: {checkpoint_path} (epoch {epoch})")
        
        return model, optimizer, epoch, metrics

    def save_model(
        self,
        model: nn.Module,
        model_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Save inference model only (no optimizer state)
        
        Args:
            model: PyTorch model
            model_name: Model name (e.g., "behavior_classifier")
            metadata: Optional metadata dict
            
        Returns:
            Path to model file
        """
        model_path = self.checkpoint_dir / f"{model_name}.pt"
        
        model_data = {
            "model_state": model.state_dict(),
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
        }
        
        if metadata:
            model_data.update(metadata)
        
        torch.save(model_data, model_path)
        print(f"✅ Model saved: {model_path}")
        
        return str(model_path)

    def load_model(
        self,
        model: nn.Module,
        model_name: str,
        device: str = "cpu",
    ) -> nn.Module:
        """
        Load inference model
        
        Args:
            model: PyTorch model instance
            model_name: Model name
            device: Device to load on
            
        Returns:
            Loaded model
        """
        model_path = self.checkpoint_dir / f"{model_name}.pt"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        model_data = torch.load(model_path, map_location=device)
        model.load_state_dict(model_data["model_state"])
        model.eval()
        
        print(f"✅ Model loaded: {model_path}")
        
        return model

    def get_best_checkpoint(self, checkpoint_name: str, metric: str = "val_loss") -> Optional[str]:
        """
        Get best checkpoint for a model
        
        Args:
            checkpoint_name: Checkpoint name prefix
            metric: Metric to compare (default: val_loss)
            
        Returns:
            Path to best checkpoint or None
        """
        checkpoint_pattern = f"{checkpoint_name}_epoch*.pt"
        checkpoints = list(self.checkpoint_dir.glob(checkpoint_pattern))
        
        if not checkpoints:
            return None
        
        best_checkpoint = None
        best_metric_value = float("inf")
        
        for cp_path in checkpoints:
            data = torch.load(cp_path, map_location="cpu")
            if metric in data["metrics"]:
                metric_value = data["metrics"][metric]
                if metric_value < best_metric_value:
                    best_metric_value = metric_value
                    best_checkpoint = str(cp_path)
        
        if best_checkpoint:
            print(f"✅ Best checkpoint: {best_checkpoint} ({metric}={best_metric_value:.4f})")
        
        return best_checkpoint

    def list_checkpoints(self, checkpoint_name: Optional[str] = None) -> list:
        """
        List available checkpoints
        
        Args:
            checkpoint_name: Filter by name (optional)
            
        Returns:
            List of checkpoint paths
        """
        if checkpoint_name:
            pattern = f"{checkpoint_name}_epoch*.pt"
        else:
            pattern = "*.pt"
        
        checkpoints = sorted(self.checkpoint_dir.glob(pattern))
        
        for cp in checkpoints:
            data = torch.load(cp, map_location="cpu")
            epoch = data.get("epoch", "?")
            timestamp = data.get("timestamp", "?")
            print(f"  {cp.name} (epoch {epoch}, {timestamp})")
        
        return [str(cp) for cp in checkpoints]

    def cleanup_old_checkpoints(self, checkpoint_name: str, keep_best: int = 3) -> None:
        """
        Remove old checkpoints, keeping best N
        
        Args:
            checkpoint_name: Checkpoint name prefix
            keep_best: Number of best checkpoints to keep
        """
        checkpoint_pattern = f"{checkpoint_name}_epoch*.pt"
        checkpoints = sorted(self.checkpoint_dir.glob(checkpoint_pattern))
        
        if len(checkpoints) > keep_best:
            to_remove = checkpoints[:-keep_best]
            
            for cp_path in to_remove:
                cp_path.unlink()
                print(f"🗑️  Removed: {cp_path.name}")

    def export_to_onnx(
        self,
        model: nn.Module,
        input_shape: Tuple,
        model_name: str,
        device: str = "cpu",
    ) -> str:
        """
        Export model to ONNX format
        
        Args:
            model: PyTorch model
            input_shape: Input tensor shape (without batch)
            model_name: Model name
            device: Device to export from
            
        Returns:
            Path to ONNX file
        """
        try:
            import onnx
        except ImportError:
            raise ImportError("ONNX requires: pip install onnx")
        
        onnx_path = self.checkpoint_dir / f"{model_name}.onnx"
        
        # Create dummy input
        dummy_input = torch.randn(1, *input_shape).to(device)
        
        # Export
        torch.onnx.export(
            model,
            dummy_input,
            str(onnx_path),
            input_names=["input"],
            output_names=["output"],
            opset_version=13,
            do_constant_folding=True,
        )
        
        print(f"✅ Model exported to ONNX: {onnx_path}")
        
        return str(onnx_path)

    def get_checkpoint_metadata(self, checkpoint_path: str) -> Dict[str, Any]:
        """
        Get metadata from checkpoint
        
        Args:
            checkpoint_path: Path to checkpoint
            
        Returns:
            Metadata dictionary
        """
        data = torch.load(checkpoint_path, map_location="cpu")
        
        return {
            "epoch": data.get("epoch"),
            "timestamp": data.get("timestamp"),
            "metrics": data.get("metrics", {}),
            "model_name": data.get("model_name"),
        }
