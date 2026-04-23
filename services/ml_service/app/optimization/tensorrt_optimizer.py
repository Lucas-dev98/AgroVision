"""
TensorRT Optimization Module (Optional)

Generates TensorRT engines for NVIDIA GPU optimization.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TensorRTOptimizer:
    """
    Generates TensorRT engines for GPU-optimized inference.

    Note: Requires TensorRT installed. This is optional for CPU-only systems.
    """

    def __init__(self, onnx_models_dir: str, output_dir: str):
        """
        Initialize TensorRT optimizer.

        Args:
            onnx_models_dir: Directory containing ONNX models
            output_dir: Directory to save TensorRT engines
        """
        self.onnx_models_dir = Path(onnx_models_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tensorrt_available = self._check_tensorrt_available()

    def _check_tensorrt_available(self) -> bool:
        """Check if TensorRT is available."""
        try:
            import tensorrt as trt
            logger.info("✅ TensorRT available")
            return True
        except ImportError:
            logger.warning(
                "⚠️  TensorRT not available (optional dependency). "
                "TensorRT optimization will be skipped."
            )
            return False

    async def build_engine(
        self, model_type: str, max_batch_size: int = 1
    ) -> Tuple[bool, str]:
        """
        Build TensorRT engine from ONNX model.

        Args:
            model_type: Type of model (behavior, anomaly, reid, temporal)
            max_batch_size: Maximum batch size for the engine

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.tensorrt_available:
            return False, "TensorRT not available"

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._build_engine_sync, model_type, max_batch_size
        )

    def _build_engine_sync(
        self, model_type: str, max_batch_size: int = 1
    ) -> Tuple[bool, str]:
        """Synchronous TensorRT engine build."""
        try:
            import tensorrt as trt

            onnx_path = self.onnx_models_dir / f"{model_type}_model.onnx"

            if not onnx_path.exists():
                return False, f"ONNX model not found: {onnx_path}"

            logger.info(f"Building TensorRT engine for {model_type}...")

            # Create TensorRT logger
            TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

            # Create builder and network
            builder = trt.Builder(TRT_LOGGER)
            network = builder.create_network(
                1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
            )
            parser = trt.OnnxParser(network, TRT_LOGGER)

            # Parse ONNX model
            with open(str(onnx_path), "rb") as f:
                if not parser.parse(f.read()):
                    errors = [parser.get_error(i) for i in range(parser.num_errors)]
                    msg = f"Failed to parse ONNX model: {errors}"
                    logger.error(msg)
                    return False, msg

            # Build engine
            config = builder.create_builder_config()
            config.max_workspace_size = 1 << 30  # 1GB
            config.set_flag(trt.BuilderFlag.GPU_FALLBACK)

            # Optional: Enable FP16
            if builder.platform_has_fast_fp16:
                config.set_flag(trt.BuilderFlag.FP16)

            engine = builder.build_engine(network, config)

            if engine is None:
                return False, "Failed to build TensorRT engine"

            # Save engine
            engine_path = self.output_dir / f"{model_type}_model.trtengine"
            with open(str(engine_path), "wb") as f:
                f.write(engine.serialize())

            engine_size = engine_path.stat().st_size
            msg = (
                f"✅ {model_type}: TensorRT engine built successfully\n"
                f"   Engine size: {engine_size/(1024*1024):.2f}MB\n"
                f"   Path: {engine_path}"
            )

            logger.info(msg)
            return True, msg

        except ImportError:
            return False, "TensorRT not installed"
        except Exception as e:
            msg = f"❌ Failed to build TensorRT engine for {model_type}: {str(e)}"
            logger.error(msg)
            return False, msg

    async def build_all_engines(
        self, max_batch_size: int = 1
    ) -> Dict[str, Dict]:
        """
        Build TensorRT engines for all models.

        Returns:
            Dictionary with build results
        """
        if not self.tensorrt_available:
            return {
                "available": False,
                "message": "TensorRT not available (optional dependency)",
            }

        results = {}
        model_types = ["behavior", "anomaly", "reid", "temporal"]

        for model_type in model_types:
            logger.info(f"\nBuilding TensorRT engine for {model_type}...")
            success, message = await self.build_engine(model_type, max_batch_size)
            results[model_type] = {"success": success, "message": message}

        return results

    @staticmethod
    def get_tensorrt_status() -> Dict:
        """Get TensorRT availability and version info."""
        try:
            import tensorrt as trt

            return {
                "available": True,
                "version": trt.__version__,
                "status": "Ready for optimization",
            }
        except ImportError:
            return {
                "available": False,
                "version": None,
                "status": "Not installed (optional)",
            }
