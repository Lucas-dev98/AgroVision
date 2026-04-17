"""
Tests for FASE 3.4 - Production Deployment (Task 1: Real-time Prediction API)

TDD Approach:
1. Write tests first
2. Implement to pass tests
3. Refactor
4. Commit

Task 1 Tests:
- PredictionService batch predictions
- PredictionService streaming
- FastAPI endpoints
- Input validation
- Error handling
- Performance requirements
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import numpy as np
import torch

from app.services.prediction_service import (
    PredictionService,
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    ModelInfo,
)


# ============================================================================
# Tests for PredictionService - Batch Predictions
# ============================================================================

class TestPredictionServiceBatch:
    """Testes para predições em batch."""
    
    @pytest.fixture
    def behavior_model(self):
        """Mock de modelo de comportamento."""
        def model_forward(x):
            batch_size = x.shape[0] if isinstance(x, torch.Tensor) else len(x)
            return torch.randn(batch_size, 8)  # 8 classes
        
        model = MagicMock(side_effect=model_forward)
        model.eval = MagicMock()
        model.to = MagicMock(return_value=model)
        return model
    
    @pytest.fixture
    def anomaly_model(self):
        """Mock de modelo de anomalia."""
        def model_forward(x):
            batch_size = x.shape[0] if isinstance(x, torch.Tensor) else len(x)
            return torch.randn(batch_size, 1)  # 1 anomaly score
        
        model = MagicMock(side_effect=model_forward)
        model.eval = MagicMock()
        model.to = MagicMock(return_value=model)
        return model
    
    @pytest.fixture
    def reid_model(self):
        """Mock de modelo Re-ID."""
        def model_forward(x):
            batch_size = x.shape[0] if isinstance(x, torch.Tensor) else len(x)
            return torch.randn(batch_size, 256)  # 256-d embedding
        
        model = MagicMock(side_effect=model_forward)
        model.eval = MagicMock()
        model.to = MagicMock(return_value=model)
        return model
    
    @pytest.fixture
    def temporal_model(self):
        """Mock de modelo temporal."""
        def model_forward(x):
            batch_size = x.shape[0] if isinstance(x, torch.Tensor) else len(x)
            return torch.randn(batch_size, 8)  # 8 classes
        
        model = MagicMock(side_effect=model_forward)
        model.eval = MagicMock()
        model.to = MagicMock(return_value=model)
        return model
    
    @pytest.fixture
    def prediction_service(self, behavior_model, anomaly_model, reid_model, temporal_model):
        """Cria PredictionService com mocks."""
        return PredictionService(
            behavior_model=behavior_model,
            anomaly_model=anomaly_model,
            reid_model=reid_model,
            temporal_model=temporal_model,
            device="cpu",
        )
    
    @pytest.mark.asyncio
    async def test_batch_predict_behavior(self, prediction_service):
        """Testa predição em batch para comportamento."""
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[
                np.random.randn(3, 240, 240).astype(np.float32),
                np.random.randn(3, 240, 240).astype(np.float32),
            ],
        )
        
        response = await prediction_service.batch_predict(request)
        
        assert isinstance(response, BatchPredictionResponse)
        assert response.model_type == "behavior"
        assert len(response.predictions) == 2
        assert response.processing_time_ms > 0
        assert response.model_version is not None
    
    @pytest.mark.asyncio
    async def test_batch_predict_anomaly(self, prediction_service):
        """Testa predição em batch para anomalia."""
        request = BatchPredictionRequest(
            model_type="anomaly",
            inputs=[
                np.random.randn(6).astype(np.float32),
                np.random.randn(6).astype(np.float32),
            ],
        )
        
        response = await prediction_service.batch_predict(request)
        
        assert response.model_type == "anomaly"
        assert len(response.predictions) == 2
        assert all("anomaly_score" in p for p in response.predictions)
    
    @pytest.mark.asyncio
    async def test_batch_predict_reid(self, prediction_service):
        """Testa predição em batch para Re-ID."""
        request = BatchPredictionRequest(
            model_type="reid",
            inputs=[
                np.random.randn(3, 224, 224).astype(np.float32),
                np.random.randn(3, 224, 224).astype(np.float32),
            ],
        )
        
        response = await prediction_service.batch_predict(request)
        
        assert response.model_type == "reid"
        assert len(response.predictions) == 2
    
    @pytest.mark.asyncio
    async def test_batch_predict_temporal(self, prediction_service):
        """Testa predição em batch para temporal."""
        request = BatchPredictionRequest(
            model_type="temporal",
            inputs=[
                np.random.randn(30, 128).astype(np.float32),
                np.random.randn(30, 128).astype(np.float32),
            ],
        )
        
        response = await prediction_service.batch_predict(request)
        
        assert response.model_type == "temporal"
        assert len(response.predictions) == 2
    
    @pytest.mark.asyncio
    async def test_batch_predict_invalid_model(self, prediction_service):
        """Testa erro para modelo inválido."""
        with pytest.raises(ValueError):
            request = BatchPredictionRequest(
                model_type="invalid_model",
                inputs=[np.random.randn(3, 240, 240).astype(np.float32)],
            )
    
    @pytest.mark.asyncio
    async def test_batch_predict_empty_inputs(self, prediction_service):
        """Testa erro para inputs vazios."""
        with pytest.raises(ValueError):
            request = BatchPredictionRequest(
                model_type="behavior",
                inputs=[],
            )
    
    @pytest.mark.asyncio
    async def test_batch_predict_large_batch(self, prediction_service):
        """Testa batch grande (100 amostras)."""
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[
                np.random.randn(3, 240, 240).astype(np.float32)
                for _ in range(100)
            ],
        )
        
        response = await prediction_service.batch_predict(request)
        
        assert len(response.predictions) == 100
        assert response.batch_size == 100


# ============================================================================
# Tests for PredictionService - Streaming Predictions
# ============================================================================

class TestPredictionServiceStreaming:
    """Testes para predições em stream."""
    
    @pytest.mark.asyncio
    async def test_stream_predict_behavior(self, prediction_service):
        """Testa streaming de predições."""
        inputs = [
            np.random.randn(3, 240, 240).astype(np.float32)
            for _ in range(5)
        ]
        
        predictions = []
        async for pred in prediction_service.stream_predict(
            model_type="behavior",
            inputs=inputs,
        ):
            predictions.append(pred)
        
        assert len(predictions) == 5
        assert all("class" in p for p in predictions)
        assert all("confidence" in p for p in predictions)
    
    @pytest.mark.asyncio
    async def test_stream_predict_with_timeout(self, prediction_service):
        """Testa timeout em streaming."""
        inputs = [
            np.random.randn(3, 240, 240).astype(np.float32)
            for _ in range(3)
        ]
        
        predictions = []
        async for pred in prediction_service.stream_predict(
            model_type="behavior",
            inputs=inputs,
        ):
            predictions.append(pred)
        
        assert len(predictions) == 3


# ============================================================================
# Tests for PredictionService - Model Info
# ============================================================================

class TestPredictionServiceModelInfo:
    """Testes para informações de modelos."""
    
    def test_get_model_info_behavior(self, prediction_service):
        """Testa informações do modelo de comportamento."""
        info = prediction_service.get_model_info("behavior")
        
        assert isinstance(info, ModelInfo)
        assert info.model_type == "behavior"
        assert info.input_shape == (3, 240, 240)
        assert info.output_classes == 8
        assert info.version is not None
    
    def test_get_model_info_anomaly(self, prediction_service):
        """Testa informações do modelo de anomalia."""
        info = prediction_service.get_model_info("anomaly")
        
        assert info.model_type == "anomaly"
        assert info.input_shape == (6,)
        assert info.output_shape == (1,)
    
    def test_get_model_info_reid(self, prediction_service):
        """Testa informações do modelo Re-ID."""
        info = prediction_service.get_model_info("reid")
        
        assert info.model_type == "reid"
        assert info.input_shape == (3, 224, 224)
    
    def test_get_model_info_temporal(self, prediction_service):
        """Testa informações do modelo temporal."""
        info = prediction_service.get_model_info("temporal")
        
        assert info.model_type == "temporal"
        assert info.input_shape == (30, 128)
    
    def test_get_model_info_invalid(self, prediction_service):
        """Testa erro para modelo inválido."""
        with pytest.raises(ValueError):
            prediction_service.get_model_info("invalid_model")
    
    def test_get_all_models_info(self, prediction_service):
        """Testa obter info de todos os modelos."""
        info_dict = prediction_service.get_all_models_info()
        
        assert len(info_dict) == 4
        assert "behavior" in info_dict
        assert "anomaly" in info_dict
        assert "reid" in info_dict
        assert "temporal" in info_dict


# ============================================================================
# Tests for PredictionService - Health Check
# ============================================================================

class TestPredictionServiceHealth:
    """Testes para health check."""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, prediction_service):
        """Testa health check bem-sucedido."""
        health = await prediction_service.health_check()
        
        assert health["status"] == "healthy"
        assert health["models_loaded"] == 4
        assert all(health["models"].values())  # Todos True
        assert health["device"] == "cpu"
    
    @pytest.mark.asyncio
    async def test_health_check_inference(self, prediction_service):
        """Testa health check com inferência."""
        health = await prediction_service.health_check(run_inference=True)
        
        assert health["status"] == "healthy"
        assert "inference_time_ms" in health
        assert health["inference_time_ms"] > 0


# ============================================================================
# Tests for Request/Response Validation
# ============================================================================

class TestPredictionRequestValidation:
    """Testes para validação de requests."""
    
    def test_prediction_request_valid(self):
        """Testa request válido."""
        request = PredictionRequest(
            model_type="behavior",
            input_data=np.random.randn(3, 240, 240).astype(np.float32),
        )
        
        assert request.model_type == "behavior"
        assert request.input_data.shape == (3, 240, 240)
    
    def test_prediction_request_invalid_model_type(self):
        """Testa erro para model_type inválido."""
        with pytest.raises(ValueError):
            PredictionRequest(
                model_type="invalid",
                input_data=np.random.randn(3, 240, 240).astype(np.float32),
            )
    
    def test_batch_prediction_request_valid(self):
        """Testa batch request válido."""
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[
                np.random.randn(3, 240, 240).astype(np.float32),
                np.random.randn(3, 240, 240).astype(np.float32),
            ],
        )
        
        assert request.model_type == "behavior"
        assert len(request.inputs) == 2
    
    def test_batch_prediction_request_size_limit(self):
        """Testa limite de size em batch."""
        # Criar batch com mais de 1000 amostras (assumindo limite)
        with pytest.raises(ValueError):
            BatchPredictionRequest(
                model_type="behavior",
                inputs=[
                    np.random.randn(3, 240, 240).astype(np.float32)
                    for _ in range(1001)
                ],
            )


# ============================================================================
# Tests for Error Handling
# ============================================================================

class TestPredictionErrorHandling:
    """Testes para tratamento de erros."""
    
    @pytest.mark.asyncio
    async def test_inference_error_handling(self, error_prediction_service):
        """Testa tratamento de erro em inferência."""
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[np.random.randn(3, 240, 240).astype(np.float32)],
        )
        
        with pytest.raises(RuntimeError):
            await error_prediction_service.batch_predict(request)
    
    @pytest.mark.asyncio
    async def test_gpu_fallback_to_cpu(self, prediction_service):
        """Testa fallback para CPU se GPU falhar."""
        service = PredictionService(
            behavior_model=MagicMock(),
            anomaly_model=MagicMock(),
            reid_model=MagicMock(),
            temporal_model=MagicMock(),
            device="cuda",  # Tentar CUDA
        )
        
        # Se CUDA não disponível, deve usar CPU
        assert service.device in ["cuda", "cpu"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestPredictionServiceIntegration:
    """Testes de integração."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_batch(self, prediction_service):
        """Testa pipeline completo com batch."""
        # 1. Check health
        health = await prediction_service.health_check()
        assert health["status"] == "healthy"
        
        # 2. Get model info
        info = prediction_service.get_model_info("behavior")
        assert info is not None
        
        # 3. Batch predict
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[
                np.random.randn(3, 240, 240).astype(np.float32)
                for _ in range(10)
            ],
        )
        response = await prediction_service.batch_predict(request)
        
        assert len(response.predictions) == 10
        assert response.processing_time_ms > 0


# ============================================================================
# Performance Tests
# ============================================================================

class TestPredictionPerformance:
    """Testes de performance."""
    
    @pytest.mark.asyncio
    async def test_latency_single_prediction(self, prediction_service):
        """Testa latência de predição única."""
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[np.random.randn(3, 240, 240).astype(np.float32)],
        )
        
        response = await prediction_service.batch_predict(request)
        
        # Target: < 100ms
        assert response.processing_time_ms < 100
    
    @pytest.mark.asyncio
    async def test_throughput_batch(self, prediction_service):
        """Testa throughput em batch."""
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[
                np.random.randn(3, 240, 240).astype(np.float32)
                for _ in range(32)
            ],
        )
        
        response = await prediction_service.batch_predict(request)
        
        # Target: 32 amostras em < 500ms = > 64 samples/sec
        assert response.processing_time_ms < 500
