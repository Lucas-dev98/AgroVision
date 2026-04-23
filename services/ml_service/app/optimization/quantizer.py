"""
Model Quantization Module

Implements INT8 and FP16 quantization for reduced model size and latency.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

import torch
import torch.quantization as quantization
import numpy as np
import onnxruntime as ort

logger = logging.getLogger(__name__)


class Quantizer:
    """Quantizes models to INT8 and FP16 formats."""

    def __init__(self, models_dir: str, output_dir: str):
        """
        Initialize quantizer.

        Args:
            models_dir: Directory containing PyTorch models
            output_dir: Directory to save quantized models
        """
        self.models_dir = Path(models_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.quantization_stats: Dict[str, Dict] = {}

    async def quantize_int8(
        self, model_type: str, device: str = "cpu"
    ) -> Tuple[bool, str]:
        """
        Quantize model to INT8 (maximum compression).

        Args:
            model_type: Type of model (behavior, anomaly, reid, temporal)
            device: Device to use (cpu or cuda)

        Returns:
            Tuple of (success: bool, message: str)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._quantize_int8_sync, model_type, device
        )

    def _quantize_int8_sync(
        self, model_type: str, device: str = "cpu"
    ) -> Tuple[bool, str]:
        """Synchronous INT8 quantization."""
        try:
            model_path = self.models_dir / f"{model_type}_model.pt"

            if not model_path.exists():
                return False, f"Model not found: {model_path}"

            logger.info(f"Loading {model_type} model for INT8 quantization...")
            model = torch.load(model_path, map_location=device)
            model.eval()

            # Prepare quantization config
            model.qconfig = quantization.get_default_qconfig("fbgemm")
            quantization.prepare(model, inplace=True)

            # Calibrate (in production, use representative data)
            # For now, just dummy data
            logger.info("Calibrating INT8 quantization...")
            self._calibrate_model(model, model_type, device)

            # Convert to INT8
            logger.info("Converting to INT8...")
            quantization.convert(model, inplace=True)

            # Save quantized model
            quantized_path = self.output_dir / f"{model_type}_model_int8.pt"
            torch.save(model, str(quantized_path))

            # Get sizes
            original_size = model_path.stat().st_size
            quantized_size = quantized_path.stat().st_size
            compression_ratio = (1 - quantized_size / original_size) * 100

            # Validate quantized model
            validation_ok = self._validate_quantized_model(
                model_path, quantized_path, model_type, device
            )

            stats = {
                "original_size_mb": original_size / (1024 * 1024),
                "quantized_size_mb": quantized_size / (1024 * 1024),
                "compression_percent": compression_ratio,
                "validation_ok": validation_ok,
                "quantized_path": str(quantized_path),
            }

            self.quantization_stats[f"{model_type}_int8"] = stats

            msg = (
                f"✅ {model_type} INT8: Quantized successfully\n"
                f"   Size: {original_size/(1024*1024):.2f}MB → {quantized_size/(1024*1024):.2f}MB "
                f"({compression_ratio:.1f}% compression)\n"
                f"   Validation: {'PASSED' if validation_ok else 'WARNING'}"
            )

            logger.info(msg)
            return True, msg

        except Exception as e:
            msg = f"❌ Failed to quantize {model_type} to INT8: {str(e)}"
            logger.error(msg)
            return False, msg

    async def quantize_fp16(
        self, model_type: str, device: str = "cpu"
    ) -> Tuple[bool, str]:
        """
        Quantize model to FP16 (good balance of size and accuracy).

        Args:
            model_type: Type of model (behavior, anomaly, reid, temporal)
            device: Device to use (cpu or cuda)

        Returns:
            Tuple of (success: bool, message: str)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._quantize_fp16_sync, model_type, device
        )

    def _quantize_fp16_sync(
        self, model_type: str, device: str = "cpu"
    ) -> Tuple[bool, str]:
        """Synchronous FP16 quantization."""
        try:
            model_path = self.models_dir / f"{model_type}_model.pt"

            if not model_path.exists():
                return False, f"Model not found: {model_path}"

            logger.info(f"Loading {model_type} model for FP16 quantization...")
            model = torch.load(model_path, map_location=device)
            model.eval()
            model = model.half()  # Convert to FP16

            # Save quantized model
            quantized_path = self.output_dir / f"{model_type}_model_fp16.pt"
            torch.save(model, str(quantized_path))

            # Get sizes
            original_size = model_path.stat().st_size
            quantized_size = quantized_path.stat().st_size
            compression_ratio = (1 - quantized_size / original_size) * 100

            # Validate
            validation_ok = self._validate_quantized_model(
                model_path, quantized_path, model_type, device
            )

            stats = {
                "original_size_mb": original_size / (1024 * 1024),
                "quantized_size_mb": quantized_size / (1024 * 1024),
                "compression_percent": compression_ratio,
                "validation_ok": validation_ok,
                "quantized_path": str(quantized_path),
            }

            self.quantization_stats[f"{model_type}_fp16"] = stats

            msg = (
                f"✅ {model_type} FP16: Quantized successfully\n"
                f"   Size: {original_size/(1024*1024):.2f}MB → {quantized_size/(1024*1024):.2f}MB "
                f"({compression_ratio:.1f}% compression)\n"
                f"   Validation: {'PASSED' if validation_ok else 'WARNING'}"
            )

            logger.info(msg)
            return True, msg

        except Exception as e:
            msg = f"❌ Failed to quantize {model_type} to FP16: {str(e)}"
            logger.error(msg)
            return False, msg

    def _calibrate_model(
        self, model: torch.nn.Module, model_type: str, device: str
    ):
        """Calibrate model with dummy data (in production, use real data)."""
        model.eval()
        with torch.no_grad():
            if model_type == "behavior":
                dummy_data = torch.randn(8, 3, 240, 240, device=device)
            elif model_type == "anomaly":
                dummy_data = torch.randn(8, 6, device=device)
            elif model_type == "reid":
                dummy_data = torch.randn(8, 3, 224, 224, device=device)
            elif model_type == "temporal":
                dummy_data = torch.randn(8, 30, 128, device=device)
            else:
                dummy_data = torch.randn(8, 3, 224, 224, device=device)

            model(dummy_data)

    def _validate_quantized_model(
        self, original_path: Path, quantized_path: Path, model_type: str, device: str
    ) -> bool:
        """
        Validate that quantized model still works.

        Returns:
            bool: True if validation passes
        """
        try:
            original_model = torch.load(original_path, map_location=device)
            quantized_model = torch.load(quantized_path, map_location=device)

            original_model.eval()
            quantized_model.eval()

            # Test with dummy input
            with torch.no_grad():
                if model_type == "behavior":
                    dummy_data = torch.randn(1, 3, 240, 240, device=device)
                elif model_type == "anomaly":
                    dummy_data = torch.randn(1, 6, device=device)
                elif model_type == "reid":
                    dummy_data = torch.randn(1, 3, 224, 224, device=device)
                elif model_type == "temporal":
                    dummy_data = torch.randn(1, 30, 128, device=device)
                else:
                    dummy_data = torch.randn(1, 3, 224, 224, device=device)

                original_output = original_model(dummy_data)
                if isinstance(original_output, tuple):
                    original_output = original_output[0]

                quantized_output = quantized_model(dummy_data)
                if isinstance(quantized_output, tuple):
                    quantized_output = quantized_output[0]

                # Check if outputs have similar shapes
                if original_output.shape != quantized_output.shape:
                    logger.warning(
                        f"Shape mismatch: {original_output.shape} vs {quantized_output.shape}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False

    async def quantize_all_models(
        self, device: str = "cpu"
    ) -> Dict[str, Dict]:
        """
        Quantize all models to INT8 and FP16.

        Returns:
            Dictionary with quantization results
        """
        results = {}
        model_types = ["behavior", "anomaly", "reid", "temporal"]

        for model_type in model_types:
            logger.info(f"\n===== Quantizing {model_type} =====")

            # INT8
            int8_success, int8_msg = await self.quantize_int8(model_type, device)
            results[f"{model_type}_int8"] = {
                "success": int8_success,
                "message": int8_msg,
            }

            # FP16
            fp16_success, fp16_msg = await self.quantize_fp16(model_type, device)
            results[f"{model_type}_fp16"] = {
                "success": fp16_success,
                "message": fp16_msg,
            }

        return results

    def get_quantization_summary(self) -> Dict:
        """Get summary of all quantization results."""
        int8_total_mb = sum(
            s["quantized_size_mb"]
            for k, s in self.quantization_stats.items()
            if "int8" in k
        )
        fp16_total_mb = sum(
            s["quantized_size_mb"]
            for k, s in self.quantization_stats.items()
            if "fp16" in k
        )

        return {
            "total_quantization_results": len(self.quantization_stats),
            "int8_total_size_mb": int8_total_mb,
            "fp16_total_size_mb": fp16_total_mb,
            "models": self.quantization_stats,
        }
