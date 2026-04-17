"""
Tests for FASE 3.2 - Training Integration

Testa:
- Data Sync Service
- Incremental Trainer
- Data Quality Dashboard
- Training script integration
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import json

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.data.data_sync import DataSyncService, IncrementalDataManager
from app.training.incremental_trainer import IncrementalTrainer
from app.monitoring.data_dashboard import DataQualityDashboard


# ============================================================================
# Tests for DataSyncService
# ============================================================================

class TestDataSyncService:
    """Testes para o serviço de sincronização de dados."""
    
    @pytest.mark.asyncio
    async def test_init_creates_metrics(self):
        """Verifica se inicialização cria métricas para cada coleção."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        sync_service = DataSyncService(db, sync_interval_minutes=30)
        
        assert len(sync_service.metrics) == 4
        assert "tracking" in sync_service.metrics
        assert "behavior_patterns" in sync_service.metrics
        assert "animal_health" in sync_service.metrics
        assert "animal_reid" in sync_service.metrics
    
    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Verifica se pode iniciar e parar o serviço."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        sync_service = DataSyncService(db)
        
        assert not sync_service.is_running
        
        await sync_service.start()
        assert sync_service.is_running
        
        await asyncio.sleep(0.1)
        await sync_service.stop()
        assert not sync_service.is_running
    
    @pytest.mark.asyncio
    async def test_get_sync_metrics(self):
        """Verifica se obtém métricas de sincronização."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        sync_service = DataSyncService(db)
        
        metrics = await sync_service.get_sync_metrics()
        
        assert isinstance(metrics, dict)
        assert "tracking" in metrics
        assert "status" in metrics["tracking"]
    
    @pytest.mark.asyncio
    async def test_get_sync_status(self):
        """Verifica se obtém status geral do serviço."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        sync_service = DataSyncService(db)
        
        status = await sync_service.get_sync_status()
        
        assert status["is_running"] == False
        assert status["sync_interval_minutes"] == 30
        assert status["collections_monitored"] == 4


class TestIncrementalDataManager:
    """Testes para o gerenciador de dados incrementais."""
    
    @pytest.mark.asyncio
    async def test_mark_data_trained(self):
        """Verifica se marca dados como treinados."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        db.__getitem__.return_value.insert_one = AsyncMock()
        
        manager = IncrementalDataManager(db)
        
        await manager.mark_data_trained(
            collection_name="tracking",
            document_ids=["doc1", "doc2"],
            model_name="behavior_model",
            epoch=1,
        )
        
        db["training_logs"].insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_new_data(self):
        """Verifica se obtém dados novos não treinados."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        
        # Mock da coleção de training_logs
        training_logs_mock = AsyncMock()
        training_logs_mock.find.return_value.to_list = AsyncMock(return_value=[
            {
                "collection": "tracking",
                "document_ids": ["doc1"],
                "model_name": "behavior",
                "timestamp": datetime.now(),
            }
        ])
        
        # Mock da coleção de tracking
        tracking_mock = AsyncMock()
        tracking_mock.find.return_value.to_list = AsyncMock(return_value=[
            {"_id": "doc2", "timestamp": datetime.now()},
            {"_id": "doc3", "timestamp": datetime.now()},
        ])
        
        db.__getitem__.side_effect = lambda name: (
            training_logs_mock if name == "training_logs" else tracking_mock
        )
        
        manager = IncrementalDataManager(db)
        
        new_data = await manager.get_new_data(
            collection_name="tracking",
            model_name="behavior",
            since_hours=24,
        )
        
        assert len(new_data) == 2


# ============================================================================
# Tests for IncrementalTrainer
# ============================================================================

class TestIncrementalTrainer:
    """Testes para o treinador incremental."""
    
    def test_init(self):
        """Verifica se inicializa corretamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = IncrementalTrainer(
                model_path=f"{tmpdir}/model.pt",
                checkpoint_dir=f"{tmpdir}/checkpoints",
            )
            
            assert trainer.use_real_data == False
            assert len(trainer.training_history["epochs"]) == 0
    
    def test_get_start_epoch_no_history(self):
        """Verifica se retorna epoch 0 sem histórico."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = IncrementalTrainer(
                model_path=f"{tmpdir}/model.pt",
                checkpoint_dir=f"{tmpdir}/checkpoints",
            )
            
            assert trainer.get_start_epoch() == 0
    
    def test_get_start_epoch_with_history(self):
        """Verifica se retorna próxima época com histórico."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = IncrementalTrainer(
                model_path=f"{tmpdir}/model.pt",
                checkpoint_dir=f"{tmpdir}/checkpoints",
            )
            
            trainer.training_history["epochs"] = [0, 1, 2]
            
            assert trainer.get_start_epoch() == 3
    
    def test_get_checkpoint_path(self):
        """Verifica se gera caminho correto para checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = IncrementalTrainer(
                model_path=f"{tmpdir}/model.pt",
                checkpoint_dir=f"{tmpdir}/checkpoints",
            )
            
            path = trainer.get_checkpoint_path(5)
            
            assert "checkpoint_epoch_0005.pt" in str(path)
    
    def test_record_epoch(self):
        """Verifica se registra épocas corretamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = IncrementalTrainer(
                model_path=f"{tmpdir}/model.pt",
                checkpoint_dir=f"{tmpdir}/checkpoints",
            )
            
            trainer.record_epoch(0, 0.5, 0.4, 0.85, 0.95)
            
            assert len(trainer.training_history["epochs"]) == 1
            assert trainer.training_history["epochs"][0] == 0
            assert trainer.training_history["train_loss"][0] == 0.5
            assert trainer.training_history["val_loss"][0] == 0.4
            assert trainer.training_history["val_accuracy"][0] == 0.85
    
    def test_get_training_summary(self):
        """Verifica sumário de treinamento."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = IncrementalTrainer(
                model_path=f"{tmpdir}/model.pt",
                checkpoint_dir=f"{tmpdir}/checkpoints",
            )
            
            trainer.training_history["epochs"] = [0, 1]
            trainer.training_history["train_loss"] = [0.5, 0.4]
            trainer.training_history["val_loss"] = [0.5, 0.4]
            trainer.training_history["val_accuracy"] = [0.8, 0.85]
            
            summary = trainer.get_training_summary()
            
            assert summary["total_epochs"] == 2
            assert summary["best_val_accuracy"] == 0.85
            assert summary["average_val_accuracy"] == 0.825


# ============================================================================
# Tests for DataQualityDashboard
# ============================================================================

class TestDataQualityDashboard:
    """Testes para o dashboard de qualidade de dados."""
    
    def test_init(self):
        """Verifica se inicializa corretamente."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        dashboard = DataQualityDashboard(db)
        
        assert dashboard.db == db
        assert dashboard.thresholds["min_records_per_collection"] == 100
        assert dashboard.thresholds["min_quality_score"] == 0.85
    
    def test_check_alerts_empty_history(self):
        """Verifica se retorna lista vazia sem histórico."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        dashboard = DataQualityDashboard(db)
        
        alerts = dashboard.check_alerts()
        
        assert alerts == []
    
    def test_get_dashboard_summary_no_data(self):
        """Verifica sumário sem dados."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        dashboard = DataQualityDashboard(db)
        
        summary = dashboard.get_dashboard_summary()
        
        assert summary["status"] == "no_data"
    
    def test_export_metrics(self):
        """Verifica se exporta métricas para arquivo."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        dashboard = DataQualityDashboard(db)
        
        # Adicionar alguns dados
        dashboard.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            "quality": {"overall_quality_score": 0.95},
            "statistics": {"collections": {}},
        })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = f"{tmpdir}/metrics.json"
            dashboard.export_metrics(export_path)
            
            assert Path(export_path).exists()
            
            with open(export_path) as f:
                data = json.load(f)
            
            assert "export_time" in data
            assert "metrics_count" in data


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase32Integration:
    """Testes de integração para Phase 3.2."""
    
    @pytest.mark.asyncio
    async def test_sync_service_lifecycle(self):
        """Testa ciclo de vida completo do serviço de sincronização."""
        db = MagicMock(spec=AsyncIOMotorDatabase)
        
        # Mock collection
        collection_mock = AsyncMock()
        collection_mock.count_documents = AsyncMock(return_value=100)
        collection_mock.find = AsyncMock(return_value=AsyncMock())
        collection_mock.find.return_value.__aiter__ = AsyncMock(return_value=iter([]))
        collection_mock.update_one = AsyncMock()
        collection_mock.delete_many = AsyncMock(return_value=MagicMock(deleted_count=0))
        
        db.__getitem__.return_value = collection_mock
        
        sync_service = DataSyncService(db, sync_interval_minutes=1)
        
        await sync_service.start()
        await asyncio.sleep(0.2)
        await sync_service.stop()
    
    def test_trainer_checkpoint_workflow(self):
        """Testa fluxo de checkpoints no treinador."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trainer = IncrementalTrainer(
                model_path=f"{tmpdir}/model.pt",
                checkpoint_dir=f"{tmpdir}/checkpoints",
            )
            
            # Simular treinamento
            for epoch in range(3):
                trainer.record_epoch(
                    epoch=epoch,
                    train_loss=0.5 - epoch * 0.1,
                    val_loss=0.4 - epoch * 0.08,
                    val_accuracy=0.80 + epoch * 0.05,
                )
            
            # Verificar histórico
            assert len(trainer.training_history["epochs"]) == 3
            assert trainer.get_start_epoch() == 3
            
            # Verificar se salva histórico
            trainer._save_history()
            assert trainer.history_file.exists()
            
            # Criar novo trainer e carregar histórico
            trainer2 = IncrementalTrainer(
                model_path=f"{tmpdir}/model.pt",
                checkpoint_dir=f"{tmpdir}/checkpoints",
            )
            
            assert len(trainer2.training_history["epochs"]) == 3


# ============================================================================
# Performance Tests
# ============================================================================

class TestPhase32Performance:
    """Testes de performance para Phase 3.2."""
    
    @pytest.mark.asyncio
    async def test_sync_service_performance(self):
        """Verifica performance do serviço de sincronização."""
        import time
        
        db = MagicMock(spec=AsyncIOMotorDatabase)
        collection_mock = AsyncMock()
        collection_mock.count_documents = AsyncMock(return_value=1000)
        collection_mock.find = AsyncMock(return_value=AsyncMock())
        collection_mock.find.return_value.__aiter__ = AsyncMock(return_value=iter([]))
        collection_mock.update_one = AsyncMock()
        collection_mock.delete_many = AsyncMock(return_value=MagicMock(deleted_count=0))
        
        db.__getitem__.return_value = collection_mock
        
        sync_service = DataSyncService(db)
        
        start_time = time.time()
        await sync_service.sync_collection("tracking")
        duration = time.time() - start_time
        
        # Deve completar em menos de 5 segundos
        assert duration < 5.0
