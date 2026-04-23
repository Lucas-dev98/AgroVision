"""
ONNX Exporter for PyTorch Models

Exports trained PyTorch models to ONNX format for cross-platform compatibility
and hardware acceleration.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

import torch
import torch.onnx
import numpy as np
import onnx
import onnxruntime as ort

logger = logging.getLogger(__name__)


class ONNXExporter:
    """Exports PyTorch models to ONNX format with validation."""

    # Model input specifications
    MODEL_SPECS = {
        "behavior": {
            "input_shape": (1, 3, 240, 240),
            "input_name": "image",
            "output_name": "behavior_logits",
            "model_type": "CNNBehaviorClassifier",
        },
        "anomaly": {
            "input_shape": (1, 6),
            "input_name": "features",
            "output_name": "anomaly_score",
            "model_type": "AnomalyDetectionAutoencoder",
        },
        "reid": {
            "input_shape": (1, 3, 224, 224),
            "input_name": "image",
            "output_name": "embedding",
            "model_type": "ResNetReID",
        },
        "temporal": {
            "input_shape": (1, 30, 128),
            "input_name": "sequence",
            "output_name": "temporal_logits",
            "model_type": "LSTMTemporalAnalyzer",
        },
    }

    def __init__(self, models_dir: str, output_dir: str):
        """
        Initialize ONNX exporter.

        Args:
            models_dir: Directory containing trained PyTorch models
            output_dir: Directory to save ONNX models
        """
        self.models_dir = Path(models_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.export_stats: Dict[str, Dict] = {}

    async def export_model(
        self, model_type: str, device: str = "cpu"
    ) -> Tuple[bool, str]:
        """
        Export single model to ONNX format.

        Args:
            model_type: Type of model (behavior, anomaly, reid, temporal)
            device: Device to use (cpu or cuda)

        Returns:
            Tuple of (success: bool, message: str)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._export_model_sync, model_type, device
        )

    def _export_model_sync(
        self, model_type: str, device: str = "cpu"
    ) -> Tuple[bool, str]:
        """Synchronous model export."""
        try:
            if model_type not in self.MODEL_SPECS:
                return False, f"Unknown model type: {model_type}"

            spec = self.MODEL_SPECS[model_type]
            model_path = self.models_dir / f"{model_type}_model.pt"

            if not model_path.exists():
                return False, f"Model not found: {model_path}"

            # Load model
            logger.info(f"Loading {model_type} model from {model_path}")
            model = torch.load(model_path, map_location=device)
            model.eval()

            # Create dummy input
            dummy_input = torch.randn(spec["input_shape"], device=device)

            # ONNX export path
            onnx_path = self.output_dir / f"{model_type}_model.onnx"

            # Export to ONNX
            logger.info(f"Exporting {model_type} to ONNX format...")
            torch.onnx.export(
                model,
                dummy_input,
                str(onnx_path),
                input_names=[spec["input_name"]],
                output_names=[spec["output_name"]],
                opset_version=14,
                do_constant_folding=True,
                verbose=False,
            )

            # Load and check ONNX model
            onnx_model = onnx.load(str(onnx_path))
            onnx.checker.check_model(onnx_model)

            # Get file sizes
            pytorch_size = model_path.stat().st_size
            onnx_size = onnx_path.stat().st_size
            size_reduction = (1 - onnx_size / pytorch_size) * 100

            # Validate outputs
            validation_ok, validation_msg = self._validate_onnx_output(
                model, onnx_path, dummy_input, device, spec
            )

            self.export_stats[model_type] = {
                "pytorch_size_mb": pytorch_size / (1024 * 1024),
                "onnx_size_mb": onnx_size / (1024 * 1024),
                "size_reduction_percent": size_reduction,
                "validation_ok": validation_ok,
                "validation_message": validation_msg,
                "onnx_path": str(onnx_path),
            }

            msg = (
                f"✅ {model_type}: Exported successfully\n"
                f"   Size: {pytorch_size/(1024*1024):.2f}MB → {onnx_size/(1024*1024):.2f}MB "
                f"({size_reduction:.1f}% reduction)\n"
                f"   Validation: {validation_msg}"
            )

            logger.info(msg)
            return True, msg

        except Exception as e:
            msg = f"❌ Failed to export {model_type}: {str(e)}"
            logger.error(msg)
            return False, msg

    def _validate_onnx_output(
        self,
        pytorch_model: torch.nn.Module,
        onnx_path: Path,
        dummy_input: torch.Tensor,
        device: str,
        spec: Dict,
    ) -> Tuple[bool, str]:
        """
        Validate ONNX model output against PyTorch.

        Returns:
            Tuple of (validation_ok: bool, message: str)
        """
        try:
            # Get PyTorch output
            with torch.no_grad():
                pytorch_output = pytorch_model(dummy_input)
                if isinstance(pytorch_output, tuple):
                    pytorch_output = pytorch_output[0]
                pytorch_output = pytorch_output.cpu().numpy()

            # Get ONNX output
            session = ort.InferenceSession(str(onnx_path))
            input_name = spec["input_name"]
            onnx_input = dummy_input.cpu().numpy()
            onnx_output = session.run(
                None, {input_name: onnx_input}
            )[0]

            # Compare
            max_diff = np.max(np.abs(pytorch_output - onnx_output))
            mean_diff = np.mean(np.abs(pytorch_output - onnx_output))

            if max_diff < 1e-4:  # Acceptable threshold
                msg = f"PASSED (max_diff={max_diff:.2e}, mean_diff={mean_diff:.2e})"
                return True, msg
            else:
                msg = (
                    f"WARNING: Large diff (max={max_diff:.2e}, mean={mean_diff:.2e})"
                )
                return False, msg

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    async def export_all_models(
        self, device: str = "cpu"
    ) -> Dict[str, Dict]:
        """
        Export all models to ONNX format.

        Returns:
            Dictionary with export results for each model
        """
        results = {}

        for model_type in self.MODEL_SPECS.keys():
            logger.info(f"\nExporting {model_type}...")
            success, message = await self.export_model(model_type, device)
            results[model_type] = {
                "success": success,
                "message": message,
                "stats": self.export_stats.get(model_type, {}),
            }

        return results

    def get_export_summary(self) -> Dict:
        """Get summary of all exports."""
        total_pytorch = sum(
            s["pytorch_size_mb"] for s in self.export_stats.values()
        )
        total_onnx = sum(
            s["onnx_size_mb"] for s in self.export_stats.values()
        )
        total_reduction = (1 - total_onnx / total_pytorch) * 100 if total_pytorch > 0 else 0

        return {
            "models_exported": len(self.export_stats),
            "total_pytorch_size_mb": total_pytorch,
            "total_onnx_size_mb": total_onnx,
            "total_size_reduction_percent": total_reduction,
            "models": self.export_stats,
        }
