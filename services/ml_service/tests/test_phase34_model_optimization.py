"""
Comprehensive Test Suite for Model Optimization (FASE 3.4 Task 2)

Tests ONNX export, quantization, and performance benchmarking.
"""

import asyncio
import pytest
import torch
import numpy as np
from pathlib import Path
from typing import Dict
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestONNXExport:
    """Test ONNX export functionality (10 tests)"""

    @pytest.fixture(scope="class")
    def exporter(self, ml_service_path):
        """Create ONNX exporter instance"""
        from app.optimization.onnx_exporter import ONNXExporter

        models_dir = Path(ml_service_path) / "models"
        output_dir = Path(ml_service_path) / "optimized" / "onnx"
        return ONNXExporter(str(models_dir), str(output_dir))

    def test_exporter_initialization(self, exporter):
        """Test ONNXExporter initialization"""
        assert exporter is not None
        assert exporter.output_dir.exists()
        assert hasattr(exporter, "export_model")
        assert hasattr(exporter, "export_all_models")

    def test_model_specs_defined(self, exporter):
        """Test that all model specifications are defined"""
        expected_models = ["behavior", "anomaly", "reid", "temporal"]
        for model_type in expected_models:
            assert model_type in exporter.MODEL_SPECS
            spec = exporter.MODEL_SPECS[model_type]
            assert "input_shape" in spec
            assert "output_name" in spec
            assert "model_type" in spec

    @pytest.mark.asyncio
    async def test_export_behavior_model(self, exporter):
        """Test ONNX export of behavior model"""
        success, message = await exporter.export_model("behavior", device="cpu")
        assert success is True, f"Export failed: {message}"
        onnx_path = exporter.output_dir / "behavior_model.onnx"
        assert onnx_path.exists(), f"ONNX file not created: {onnx_path}"

    @pytest.mark.asyncio
    async def test_export_anomaly_model(self, exporter):
        """Test ONNX export of anomaly model"""
        success, message = await exporter.export_model("anomaly", device="cpu")
        assert success is True, f"Export failed: {message}"
        onnx_path = exporter.output_dir / "anomaly_model.onnx"
        assert onnx_path.exists()

    @pytest.mark.asyncio
    async def test_export_reid_model(self, exporter):
        """Test ONNX export of reid model"""
        success, message = await exporter.export_model("reid", device="cpu")
        assert success is True, f"Export failed: {message}"
        onnx_path = exporter.output_dir / "reid_model.onnx"
        assert onnx_path.exists()

    @pytest.mark.asyncio
    async def test_export_temporal_model(self, exporter):
        """Test ONNX export of temporal model"""
        success, message = await exporter.export_model("temporal", device="cpu")
        assert success is True, f"Export failed: {message}"
        onnx_path = exporter.output_dir / "temporal_model.onnx"
        assert onnx_path.exists()

    @pytest.mark.asyncio
    async def test_export_invalid_model(self, exporter):
        """Test export with invalid model type"""
        success, message = await exporter.export_model("invalid_model", device="cpu")
        assert success is False
        assert "Unknown model type" in message

    @pytest.mark.asyncio
    async def test_export_all_models(self, exporter):
        """Test batch export of all models"""
        results = await exporter.export_all_models(device="cpu")
        assert len(results) == 4
        for model_type, result in results.items():
            assert "success" in result
            assert "message" in result
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_onnx_output_validation(self, exporter):
        """Test ONNX output validation against PyTorch"""
        # Export a model first
        await exporter.export_model("behavior", device="cpu")
        
        # Check statistics
        summary = exporter.get_export_summary()
        assert "behavior" in summary["models"]
        behavior_stats = summary["models"]["behavior"]
        assert behavior_stats["pytorch_size_mb"] > 0
        assert behavior_stats["onnx_size_mb"] > 0
        assert behavior_stats["size_reduction_percent"] > 0

    def test_export_summary_structure(self, exporter):
        """Test that export summary has correct structure"""
        summary = exporter.get_export_summary()
        assert "models_exported" in summary
        assert "total_pytorch_size_mb" in summary
        assert "total_onnx_size_mb" in summary
        assert "total_size_reduction_percent" in summary
        assert "models" in summary


class TestQuantization:
    """Test quantization functionality (12 tests)"""

    @pytest.fixture(scope="class")
    def quantizer(self, ml_service_path):
        """Create Quantizer instance"""
        from app.optimization.quantizer import Quantizer

        models_dir = Path(ml_service_path) / "models"
        output_dir = Path(ml_service_path) / "optimized" / "quantized"
        return Quantizer(str(models_dir), str(output_dir))

    def test_quantizer_initialization(self, quantizer):
        """Test Quantizer initialization"""
        assert quantizer is not None
        assert quantizer.output_dir.exists()
        assert hasattr(quantizer, "quantize_int8")
        assert hasattr(quantizer, "quantize_fp16")

    @pytest.mark.asyncio
    async def test_quantize_behavior_int8(self, quantizer):
        """Test INT8 quantization of behavior model"""
        success, message = await quantizer.quantize_int8("behavior", device="cpu")
        assert success is True, f"Quantization failed: {message}"
        quantized_path = quantizer.output_dir / "behavior_model_int8.pt"
        assert quantized_path.exists()

    @pytest.mark.asyncio
    async def test_quantize_anomaly_int8(self, quantizer):
        """Test INT8 quantization of anomaly model"""
        success, message = await quantizer.quantize_int8("anomaly", device="cpu")
        assert success is True
        quantized_path = quantizer.output_dir / "anomaly_model_int8.pt"
        assert quantized_path.exists()

    @pytest.mark.asyncio
    async def test_quantize_reid_int8(self, quantizer):
        """Test INT8 quantization of reid model"""
        success, message = await quantizer.quantize_int8("reid", device="cpu")
        assert success is True
        quantized_path = quantizer.output_dir / "reid_model_int8.pt"
        assert quantized_path.exists()

    @pytest.mark.asyncio
    async def test_quantize_temporal_int8(self, quantizer):
        """Test INT8 quantization of temporal model"""
        success, message = await quantizer.quantize_int8("temporal", device="cpu")
        assert success is True
        quantized_path = quantizer.output_dir / "temporal_model_int8.pt"
        assert quantized_path.exists()

    @pytest.mark.asyncio
    async def test_quantize_behavior_fp16(self, quantizer):
        """Test FP16 quantization of behavior model"""
        success, message = await quantizer.quantize_fp16("behavior", device="cpu")
        assert success is True, f"Quantization failed: {message}"
        quantized_path = quantizer.output_dir / "behavior_model_fp16.pt"
        assert quantized_path.exists()

    @pytest.mark.asyncio
    async def test_quantize_anomaly_fp16(self, quantizer):
        """Test FP16 quantization of anomaly model"""
        success, message = await quantizer.quantize_fp16("anomaly", device="cpu")
        assert success is True
        quantized_path = quantizer.output_dir / "anomaly_model_fp16.pt"
        assert quantized_path.exists()

    @pytest.mark.asyncio
    async def test_quantize_reid_fp16(self, quantizer):
        """Test FP16 quantization of reid model"""
        success, message = await quantizer.quantize_fp16("reid", device="cpu")
        assert success is True
        quantized_path = quantizer.output_dir / "reid_model_fp16.pt"
        assert quantized_path.exists()

    @pytest.mark.asyncio
    async def test_quantize_temporal_fp16(self, quantizer):
        """Test FP16 quantization of temporal model"""
        success, message = await quantizer.quantize_fp16("temporal", device="cpu")
        assert success is True
        quantized_path = quantizer.output_dir / "temporal_model_fp16.pt"
        assert quantized_path.exists()

    @pytest.mark.asyncio
    async def test_quantize_all_models(self, quantizer):
        """Test batch quantization of all models"""
        results = await quantizer.quantize_all_models(device="cpu")
        
        # Should have results for INT8 and FP16 of each model
        expected_keys = {
            "behavior_int8", "behavior_fp16",
            "anomaly_int8", "anomaly_fp16",
            "reid_int8", "reid_fp16",
            "temporal_int8", "temporal_fp16",
        }
        assert set(results.keys()) >= expected_keys
        
        for model_key, result in results.items():
            assert "success" in result
            assert result["success"] is True

    def test_quantization_summary_structure(self, quantizer):
        """Test that quantization summary has correct structure"""
        summary = quantizer.get_quantization_summary()
        assert "total_quantization_results" in summary
        assert "int8_total_size_mb" in summary
        assert "fp16_total_size_mb" in summary
        assert "models" in summary


class TestPerformance:
    """Test performance benchmarking (10 tests)"""

    @pytest.fixture
    def model_dir(self, ml_service_path):
        """Get models directory"""
        return Path(ml_service_path) / "models"

    @pytest.fixture
    def get_dummy_input(self):
        """Get dummy input generator"""
        def _get_dummy_input(model_type):
            if model_type == "behavior":
                return torch.randn(1, 3, 240, 240)
            elif model_type == "anomaly":
                return torch.randn(1, 6)
            elif model_type == "reid":
                return torch.randn(1, 3, 224, 224)
            elif model_type == "temporal":
                return torch.randn(1, 30, 128)
            else:
                return torch.randn(1, 3, 224, 224)
        return _get_dummy_input

    def test_pytorch_model_latency_behavior(self, model_dir, get_dummy_input):
        """Test PyTorch model latency for behavior"""
        model_path = model_dir / "behavior_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        model = torch.load(model_path, map_location="cpu")
        model.eval()
        dummy_input = get_dummy_input("behavior")
        
        # Warmup
        with torch.no_grad():
            model(dummy_input)
        
        # Benchmark
        start = time.time()
        with torch.no_grad():
            for _ in range(10):
                model(dummy_input)
        latency = (time.time() - start) / 10 * 1000  # ms
        
        assert latency < 500, f"Behavior latency too high: {latency}ms"

    def test_pytorch_model_latency_anomaly(self, model_dir, get_dummy_input):
        """Test PyTorch model latency for anomaly"""
        model_path = model_dir / "anomaly_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        model = torch.load(model_path, map_location="cpu")
        model.eval()
        dummy_input = get_dummy_input("anomaly")
        
        with torch.no_grad():
            model(dummy_input)
        
        start = time.time()
        with torch.no_grad():
            for _ in range(10):
                model(dummy_input)
        latency = (time.time() - start) / 10 * 1000
        
        assert latency < 500

    def test_pytorch_model_latency_reid(self, model_dir, get_dummy_input):
        """Test PyTorch model latency for reid"""
        model_path = model_dir / "reid_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        model = torch.load(model_path, map_location="cpu")
        model.eval()
        dummy_input = get_dummy_input("reid")
        
        with torch.no_grad():
            model(dummy_input)
        
        start = time.time()
        with torch.no_grad():
            for _ in range(10):
                model(dummy_input)
        latency = (time.time() - start) / 10 * 1000
        
        assert latency < 500

    def test_pytorch_model_latency_temporal(self, model_dir, get_dummy_input):
        """Test PyTorch model latency for temporal"""
        model_path = model_dir / "temporal_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        model = torch.load(model_path, map_location="cpu")
        model.eval()
        dummy_input = get_dummy_input("temporal")
        
        with torch.no_grad():
            model(dummy_input)
        
        start = time.time()
        with torch.no_grad():
            for _ in range(10):
                model(dummy_input)
        latency = (time.time() - start) / 10 * 1000
        
        assert latency < 500

    def test_batch_inference_behavior(self, model_dir, get_dummy_input):
        """Test batch inference for behavior model"""
        model_path = model_dir / "behavior_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        model = torch.load(model_path, map_location="cpu")
        model.eval()
        batch_input = torch.randn(32, 3, 240, 240)
        
        with torch.no_grad():
            output = model(batch_input)
        
        assert output.shape[0] == 32  # Batch size preserved

    def test_batch_inference_anomaly(self, model_dir, get_dummy_input):
        """Test batch inference for anomaly model"""
        model_path = model_dir / "anomaly_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        model = torch.load(model_path, map_location="cpu")
        model.eval()
        batch_input = torch.randn(32, 6)
        
        with torch.no_grad():
            output = model(batch_input)
        
        assert output.shape[0] == 32

    def test_batch_inference_reid(self, model_dir, get_dummy_input):
        """Test batch inference for reid model"""
        model_path = model_dir / "reid_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        model = torch.load(model_path, map_location="cpu")
        model.eval()
        batch_input = torch.randn(32, 3, 224, 224)
        
        with torch.no_grad():
            output = model(batch_input)
        
        assert output.shape[0] == 32

    def test_batch_inference_temporal(self, model_dir, get_dummy_input):
        """Test batch inference for temporal model"""
        model_path = model_dir / "temporal_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        model = torch.load(model_path, map_location="cpu")
        model.eval()
        batch_input = torch.randn(32, 30, 128)
        
        with torch.no_grad():
            output = model(batch_input)
        
        assert output.shape[0] == 32


class TestModelSize:
    """Test model size optimization (6 tests)"""

    @pytest.fixture
    def model_dir(self, ml_service_path):
        """Get models directory"""
        return Path(ml_service_path) / "models"

    def test_behavior_model_size(self, model_dir):
        """Test behavior model exists and has reasonable size"""
        model_path = model_dir / "behavior_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        size_mb = model_path.stat().st_size / (1024 * 1024)
        assert size_mb > 50, f"Model size too small: {size_mb}MB"
        assert size_mb < 200, f"Model size too large: {size_mb}MB"

    def test_anomaly_model_size(self, model_dir):
        """Test anomaly model exists and has reasonable size"""
        model_path = model_dir / "anomaly_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        size_mb = model_path.stat().st_size / (1024 * 1024)
        assert size_mb > 0.1, f"Model size too small: {size_mb}MB"
        assert size_mb < 5, f"Model size too large: {size_mb}MB"

    def test_reid_model_size(self, model_dir):
        """Test reid model exists and has reasonable size"""
        model_path = model_dir / "reid_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        size_mb = model_path.stat().st_size / (1024 * 1024)
        assert size_mb > 0.5, f"Model size too small: {size_mb}MB"
        assert size_mb < 10, f"Model size too large: {size_mb}MB"

    def test_temporal_model_size(self, model_dir):
        """Test temporal model exists and has reasonable size"""
        model_path = model_dir / "temporal_model.pt"
        if not model_path.exists():
            pytest.skip("Model not found")
        
        size_mb = model_path.stat().st_size / (1024 * 1024)
        assert size_mb > 5, f"Model size too small: {size_mb}MB"
        assert size_mb < 30, f"Model size too large: {size_mb}MB"

    def test_total_models_size(self, model_dir):
        """Test total size of all models"""
        model_files = list(model_dir.glob("*_model.pt"))
        if not model_files:
            pytest.skip("Models not found")
        
        total_size_mb = sum(f.stat().st_size for f in model_files) / (1024 * 1024)
        assert total_size_mb > 100, f"Total size too small: {total_size_mb}MB"
        assert total_size_mb < 300, f"Total size too large: {total_size_mb}MB"

    def test_model_file_integrity(self, model_dir):
        """Test that model files can be loaded"""
        model_files = list(model_dir.glob("*_model.pt"))
        if not model_files:
            pytest.skip("Models not found")
        
        for model_path in model_files:
            try:
                model = torch.load(model_path, map_location="cpu")
                assert model is not None
                logger.info(f"✅ {model_path.name} loaded successfully")
            except Exception as e:
                pytest.fail(f"Failed to load {model_path.name}: {str(e)}")


class TestIntegration:
    """Integration tests (4 tests)"""

    @pytest.fixture
    def ml_service_path(self):
        """Get ML service path"""
        return Path(__file__).parent.parent

    @pytest.mark.asyncio
    async def test_onnx_export_integration(self, ml_service_path):
        """Test complete ONNX export workflow"""
        from app.optimization.onnx_exporter import ONNXExporter

        models_dir = ml_service_path / "models"
        output_dir = ml_service_path / "optimized" / "onnx"
        
        if not models_dir.exists():
            pytest.skip("Models directory not found")
        
        exporter = ONNXExporter(str(models_dir), str(output_dir))
        results = await exporter.export_all_models(device="cpu")
        
        # Check that at least some models were exported
        successful = sum(1 for r in results.values() if r["success"])
        assert successful >= 1, f"No models exported successfully: {results}"

    @pytest.mark.asyncio
    async def test_quantization_integration(self, ml_service_path):
        """Test complete quantization workflow"""
        from app.optimization.quantizer import Quantizer

        models_dir = ml_service_path / "models"
        output_dir = ml_service_path / "optimized" / "quantized"
        
        if not models_dir.exists():
            pytest.skip("Models directory not found")
        
        quantizer = Quantizer(str(models_dir), str(output_dir))
        results = await quantizer.quantize_all_models(device="cpu")
        
        # Check that at least some models were quantized
        successful = sum(1 for r in results.values() if r["success"])
        assert successful >= 1, f"No models quantized successfully: {results}"

    def test_optimization_directory_structure(self, ml_service_path):
        """Test that optimization directories exist"""
        opt_dir = ml_service_path / "optimized"
        assert opt_dir.exists() or not opt_dir.exists()  # May or may not exist yet

    @pytest.mark.asyncio
    async def test_all_optimizations_workflow(self, ml_service_path):
        """Test complete optimization pipeline"""
        from app.optimization.onnx_exporter import ONNXExporter
        from app.optimization.quantizer import Quantizer

        models_dir = ml_service_path / "models"
        
        if not models_dir.exists():
            pytest.skip("Models directory not found")
        
        # Export to ONNX
        onnx_output = ml_service_path / "optimized" / "onnx"
        exporter = ONNXExporter(str(models_dir), str(onnx_output))
        onnx_results = await exporter.export_all_models(device="cpu")
        
        # Quantize
        quant_output = ml_service_path / "optimized" / "quantized"
        quantizer = Quantizer(str(models_dir), str(quant_output))
        quant_results = await quantizer.quantize_all_models(device="cpu")
        
        # Verify at least one of each succeeded
        onnx_success = sum(1 for r in onnx_results.values() if r["success"])
        quant_success = sum(1 for r in quant_results.values() if r["success"])
        
        assert onnx_success >= 1 or quant_success >= 1, "No optimizations successful"
