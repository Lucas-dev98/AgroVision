"""
Data Sync Service - Sincronização automática de dados do MongoDB

Responsabilidades:
- Sincronização periódica de dados entre diferentes fontes
- Rastreamento de última sincronização (last_sync)
- Gerenciamento de dados obsoletos
- Logging detalhado de operações
- Recovery após falhas
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
import pytz


logger = logging.getLogger(__name__)


@dataclass
class SyncMetrics:
    """Métricas de sincronização"""
    collection: str
    records_synced: int = 0
    records_skipped: int = 0
    errors: int = 0
    duration_seconds: float = 0.0
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, failed


class DataSyncService:
    """
    Serviço de sincronização automática de dados do MongoDB.
    
    Sincroniza dados de múltiplas coleções, mantém rastreamento
    de última sincronização e suporta execução em background.
    
    Exemplo:
        ```python
        sync_service = DataSyncService(db, sync_interval_minutes=30)
        await sync_service.start()
        
        # Em background...
        metrics = await sync_service.get_sync_metrics()
        print(f"Synced: {metrics['tracking']['records_synced']}")
        
        await sync_service.stop()
        ```
    """

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        sync_interval_minutes: int = 30,
        max_age_days: int = 90,
        batch_size: int = 1000,
    ):
        """
        Inicializa o serviço de sincronização.
        
        Args:
            db: Motor AsyncIOMotorDatabase
            sync_interval_minutes: Intervalo entre sincronizações (padrão: 30 min)
            max_age_days: Máxima idade de dados antes de arquivamento (padrão: 90 dias)
            batch_size: Tamanho do batch para sincronização (padrão: 1000)
        """
        self.db = db
        self.sync_interval = timedelta(minutes=sync_interval_minutes)
        self.max_age = timedelta(days=max_age_days)
        self.batch_size = batch_size
        
        self.is_running = False
        self.sync_task: Optional[asyncio.Task] = None
        self.metrics: Dict[str, SyncMetrics] = {}
        self.last_sync_times: Dict[str, datetime] = {}
        
        # Inicializar métricas para cada coleção
        for collection in ["tracking", "behavior_patterns", "animal_health", "animal_reid"]:
            self.metrics[collection] = SyncMetrics(collection=collection)
    
    async def start(self):
        """Inicia o serviço de sincronização em background."""
        if self.is_running:
            logger.warning("Sync service already running")
            return
        
        self.is_running = True
        self.sync_task = asyncio.create_task(self._sync_loop())
        logger.info(f"Data sync service started (interval: {self.sync_interval})")
    
    async def stop(self):
        """Para o serviço de sincronização."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.sync_task:
            self.sync_task.cancel()
            try:
                await self.sync_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Data sync service stopped")
    
    async def _sync_loop(self):
        """Loop principal de sincronização."""
        while self.is_running:
            try:
                await self.sync_all()
                await asyncio.sleep(self.sync_interval.total_seconds())
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(60)  # Retry após 1 min
    
    async def sync_all(self):
        """Sincroniza todas as coleções."""
        logger.info("Starting full data sync")
        
        collections = ["tracking", "behavior_patterns", "animal_health", "animal_reid"]
        
        tasks = [
            self.sync_collection(collection)
            for collection in collections
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log resultados
        for collection, result in zip(collections, results):
            if isinstance(result, Exception):
                logger.error(f"Sync failed for {collection}: {result}")
            else:
                logger.info(f"Synced {result.records_synced} records from {collection}")
    
    async def sync_collection(self, collection_name: str) -> SyncMetrics:
        """
        Sincroniza uma coleção específica.
        
        Args:
            collection_name: Nome da coleção
            
        Returns:
            SyncMetrics com estatísticas de sincronização
        """
        metric = self.metrics[collection_name]
        metric.status = "in_progress"
        start_time = datetime.now(pytz.UTC)
        
        try:
            collection = self.db[collection_name]
            
            # Obter último timestamp de sincronização
            last_sync = self.last_sync_times.get(collection_name)
            if not last_sync:
                # Primeira sincronização: obter dados dos últimos 7 dias
                last_sync = start_time - timedelta(days=7)
            
            # Query: documentos com timestamp > last_sync
            query = {"timestamp": {"$gt": last_sync}}
            
            # Contar registros
            total_count = await collection.count_documents(query)
            
            if total_count == 0:
                metric.records_skipped = 0
                metric.records_synced = 0
                metric.errors = 0
            else:
                # Sincronizar em batches
                cursor = collection.find(query).batch_size(self.batch_size)
                
                synced = 0
                async for doc in cursor:
                    try:
                        # Marcar como sincronizado (adicionar sync_timestamp)
                        await collection.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"sync_timestamp": start_time}}
                        )
                        synced += 1
                    except Exception as e:
                        logger.error(f"Error syncing document {doc.get('_id')}: {e}")
                        metric.errors += 1
                
                metric.records_synced = synced
            
            # Limpar dados antigos
            await self._cleanup_old_data(collection_name, start_time)
            
            # Atualizar timestamp de sincronização
            self.last_sync_times[collection_name] = start_time
            metric.last_sync = start_time
            metric.next_sync = start_time + self.sync_interval
            metric.status = "completed"
            
        except Exception as e:
            logger.error(f"Failed to sync collection {collection_name}: {e}")
            metric.status = "failed"
            metric.errors += 1
        
        # Calcular duração
        metric.duration_seconds = (datetime.now(pytz.UTC) - start_time).total_seconds()
        
        return metric
    
    async def _cleanup_old_data(self, collection_name: str, current_time: datetime):
        """
        Remove dados antigos (mais antigos que max_age_days).
        
        Args:
            collection_name: Nome da coleção
            current_time: Tempo atual
        """
        try:
            collection = self.db[collection_name]
            cutoff_time = current_time - self.max_age
            
            result = await collection.delete_many({"timestamp": {"$lt": cutoff_time}})
            
            if result.deleted_count > 0:
                logger.info(
                    f"Cleaned up {result.deleted_count} old records from {collection_name}"
                )
        except Exception as e:
            logger.error(f"Error cleaning up old data in {collection_name}: {e}")
    
    async def get_sync_metrics(self) -> Dict[str, dict]:
        """
        Retorna métricas de sincronização.
        
        Returns:
            Dict com status de sincronização de cada coleção
        """
        return {
            collection: {
                "records_synced": metric.records_synced,
                "records_skipped": metric.records_skipped,
                "errors": metric.errors,
                "duration_seconds": metric.duration_seconds,
                "last_sync": metric.last_sync.isoformat() if metric.last_sync else None,
                "next_sync": metric.next_sync.isoformat() if metric.next_sync else None,
                "status": metric.status,
            }
            for collection, metric in self.metrics.items()
        }
    
    async def force_sync(self, collection_name: Optional[str] = None):
        """
        Força sincronização imediata.
        
        Args:
            collection_name: Nome da coleção (None para todas)
        """
        if collection_name:
            await self.sync_collection(collection_name)
        else:
            await self.sync_all()
    
    async def get_sync_status(self) -> Dict[str, any]:
        """
        Retorna status geral do serviço.
        
        Returns:
            Dict com status do serviço
        """
        return {
            "is_running": self.is_running,
            "sync_interval_minutes": int(self.sync_interval.total_seconds() / 60),
            "max_age_days": self.max_age.days,
            "batch_size": self.batch_size,
            "collections_monitored": len(self.metrics),
            "last_sync_times": {
                coll: ts.isoformat() if ts else None
                for coll, ts in self.last_sync_times.items()
            },
            "metrics": await self.get_sync_metrics(),
        }


class IncrementalDataManager:
    """
    Gerenciador de dados incrementais para treinamento contínuo.
    
    Rastreia quais dados já foram usados para treinamento e oferece
    apenas dados novos para incrementos de treinamento.
    
    Exemplo:
        ```python
        manager = IncrementalDataManager(db)
        await manager.mark_data_trained("tracking", batch_ids)
        
        new_data = await manager.get_new_data("tracking", since_hours=24)
        ```
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Inicializa o gerenciador de dados incrementais.
        
        Args:
            db: Motor AsyncIOMotorDatabase
        """
        self.db = db
        self.training_log_collection = "training_logs"
    
    async def initialize(self):
        """Inicializa a coleção de logs de treinamento."""
        await self.db[self.training_log_collection].create_index(
            [("collection", 1), ("timestamp", 1)],
            name="idx_training_log_collection_timestamp"
        )
        logger.info("Initialized incremental data manager")
    
    async def mark_data_trained(
        self,
        collection_name: str,
        document_ids: List[str],
        model_name: str,
        epoch: int,
    ):
        """
        Marca dados como usados para treinamento.
        
        Args:
            collection_name: Nome da coleção
            document_ids: IDs dos documentos
            model_name: Nome do modelo
            epoch: Número da época
        """
        log_entry = {
            "collection": collection_name,
            "document_ids": document_ids,
            "model_name": model_name,
            "epoch": epoch,
            "timestamp": datetime.now(pytz.UTC),
            "count": len(document_ids),
        }
        
        await self.db[self.training_log_collection].insert_one(log_entry)
        logger.info(
            f"Marked {len(document_ids)} documents from {collection_name} "
            f"as trained with {model_name} (epoch {epoch})"
        )
    
    async def get_new_data(
        self,
        collection_name: str,
        model_name: str,
        since_hours: int = 24,
    ) -> List[Dict]:
        """
        Obtém dados novos não usados para treinamento.
        
        Args:
            collection_name: Nome da coleção
            model_name: Nome do modelo
            since_hours: Buscar dados dos últimas N horas
            
        Returns:
            Lista de documentos novos
        """
        cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=since_hours)
        
        # Obter IDs já treinados
        trained_entries = await self.db[self.training_log_collection].find(
            {
                "collection": collection_name,
                "model_name": model_name,
                "timestamp": {"$gt": cutoff_time},
            }
        ).to_list(None)
        
        trained_ids = set()
        for entry in trained_entries:
            trained_ids.update(entry.get("document_ids", []))
        
        # Obter dados novos
        query = {
            "timestamp": {"$gt": cutoff_time},
            "_id": {"$nin": list(trained_ids)},
        }
        
        collection = self.db[collection_name]
        new_docs = await collection.find(query).to_list(None)
        
        logger.info(
            f"Found {len(new_docs)} new documents in {collection_name} "
            f"for model {model_name}"
        )
        
        return new_docs
    
    async def get_training_statistics(self, collection_name: str) -> Dict:
        """
        Retorna estatísticas de treinamento.
        
        Args:
            collection_name: Nome da coleção
            
        Returns:
            Dict com estatísticas
        """
        training_logs = await self.db[self.training_log_collection].find(
            {"collection": collection_name}
        ).to_list(None)
        
        total_documents_trained = sum(
            log.get("count", 0) for log in training_logs
        )
        
        models_trained = set(log.get("model_name") for log in training_logs)
        
        return {
            "collection": collection_name,
            "total_documents_trained": total_documents_trained,
            "models_trained": list(models_trained),
            "training_sessions": len(training_logs),
            "last_training": (
                max(log["timestamp"] for log in training_logs).isoformat()
                if training_logs else None
            ),
        }
