"""
Data Quality Monitoring Dashboard

Monitora a qualidade dos dados durante o treinamento:
- Estatísticas de coleções
- Tendências de qualidade
- Alertas de problemas
- Relatórios de sincronização
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.data.training_manager import RealDataTrainingManager
from app.data.data_sync import DataSyncService


logger = logging.getLogger(__name__)


class DataQualityDashboard:
    """
    Dashboard de monitoramento de qualidade de dados.
    
    Exemplo:
        ```python
        dashboard = DataQualityDashboard(db, sync_service)
        
        # Gerar relatório de qualidade
        report = await dashboard.generate_quality_report()
        print(report)
        
        # Obter métricas em tempo real
        metrics = await dashboard.get_current_metrics()
        
        # Verificar alertas
        alerts = dashboard.check_alerts()
        for alert in alerts:
            print(f"⚠️ {alert['severity']}: {alert['message']}")
        ```
    """
    
    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        sync_service: Optional[DataSyncService] = None,
    ):
        """
        Inicializa o dashboard.
        
        Args:
            db: Motor AsyncIOMotorDatabase
            sync_service: Serviço de sincronização (opcional)
        """
        self.db = db
        self.sync_service = sync_service
        self.training_manager = RealDataTrainingManager()
        
        self.alert_history: List[Dict] = []
        self.metrics_history: List[Dict] = []
        
        # Thresholds para alertas
        self.thresholds = {
            "min_records_per_collection": 100,
            "min_quality_score": 0.85,
            "max_sync_age_hours": 24,
            "min_unique_animals": 5,
        }
    
    async def connect(self):
        """Conecta ao MongoDB."""
        await self.training_manager.connect()
        logger.info("Connected data quality dashboard to MongoDB")
    
    async def disconnect(self):
        """Desconecta do MongoDB."""
        await self.training_manager.disconnect()
        logger.info("Disconnected data quality dashboard")
    
    async def get_collection_statistics(self) -> Dict:
        """
        Obtém estatísticas de todas as coleções.
        
        Returns:
            Dict com estatísticas
        """
        stats = await self.training_manager.get_data_statistics()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "collections": {},
        }
        
        for collection_name in ["tracking", "behavior_patterns", "animal_health", "animal_reid"]:
            collection = self.db[collection_name]
            count = await collection.count_documents({})
            
            # Obter intervalo de datas
            oldest = await collection.find_one(sort=[("timestamp", 1)])
            newest = await collection.find_one(sort=[("timestamp", -1)])
            
            result["collections"][collection_name] = {
                "count": count,
                "oldest_record": oldest["timestamp"].isoformat() if oldest else None,
                "newest_record": newest["timestamp"].isoformat() if newest else None,
            }
        
        return result
    
    async def get_data_quality_metrics(self) -> Dict:
        """
        Calcula métricas de qualidade de dados.
        
        Returns:
            Dict com métricas de qualidade
        """
        quality = await self.training_manager.validate_data_quality()
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "quality": quality,
        }
        
        # Calcular score geral
        total_valid = sum(
            v for k, v in quality.get("valid", {}).items()
            if isinstance(v, int)
        )
        total_invalid = sum(
            v for k, v in quality.get("invalid", {}).items()
            if isinstance(v, int)
        )
        
        total = total_valid + total_invalid
        overall_score = total_valid / total if total > 0 else 0.0
        
        metrics["overall_quality_score"] = overall_score
        metrics["total_valid_records"] = total_valid
        metrics["total_invalid_records"] = total_invalid
        
        return metrics
    
    async def get_sync_metrics(self) -> Dict:
        """
        Obtém métricas de sincronização.
        
        Returns:
            Dict com status de sincronização
        """
        if not self.sync_service:
            return {"status": "sync_service_not_available"}
        
        return await self.sync_service.get_sync_status()
    
    async def get_current_metrics(self) -> Dict:
        """
        Obtém todas as métricas atuais.
        
        Returns:
            Dict combinado com todas as métricas
        """
        stats = await self.get_collection_statistics()
        quality = await self.get_data_quality_metrics()
        sync = await self.get_sync_metrics()
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "quality": quality,
            "synchronization": sync,
        }
        
        # Manter histórico
        self.metrics_history.append(metrics)
        
        # Limitar histórico a últimas 1000 entradas
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def check_alerts(self) -> List[Dict]:
        """
        Verifica alertas de qualidade de dados.
        
        Returns:
            Lista de alertas
        """
        alerts = []
        
        if not self.metrics_history:
            return alerts
        
        latest = self.metrics_history[-1]
        
        # Verificar número de registros por coleção
        for collection_name, stats in latest["statistics"]["collections"].items():
            count = stats["count"]
            if count < self.thresholds["min_records_per_collection"]:
                alerts.append({
                    "severity": "WARNING",
                    "type": "low_record_count",
                    "message": f"{collection_name}: Only {count} records (threshold: {self.thresholds['min_records_per_collection']})",
                    "timestamp": datetime.now().isoformat(),
                })
        
        # Verificar quality score
        quality_score = latest["quality"].get("overall_quality_score", 1.0)
        if quality_score < self.thresholds["min_quality_score"]:
            alerts.append({
                "severity": "CRITICAL",
                "type": "low_quality_score",
                "message": f"Data quality score is {quality_score:.2%} (threshold: {self.thresholds['min_quality_score']:.2%})",
                "timestamp": datetime.now().isoformat(),
            })
        
        # Verificar sincronização
        if "synchronization" in latest and "last_sync_times" in latest["synchronization"]:
            sync_times = latest["synchronization"]["last_sync_times"]
            now = datetime.now()
            
            for collection_name, last_sync_str in sync_times.items():
                if last_sync_str:
                    last_sync = datetime.fromisoformat(last_sync_str)
                    age_hours = (now - last_sync).total_seconds() / 3600
                    
                    if age_hours > self.thresholds["max_sync_age_hours"]:
                        alerts.append({
                            "severity": "WARNING",
                            "type": "sync_outdated",
                            "message": f"{collection_name} last synced {age_hours:.1f} hours ago",
                            "timestamp": datetime.now().isoformat(),
                        })
        
        # Manter histórico de alertas
        self.alert_history.extend(alerts)
        
        return alerts
    
    async def generate_quality_report(self) -> str:
        """
        Gera relatório de qualidade de dados em formato de texto.
        
        Returns:
            String com relatório formatado
        """
        metrics = await self.get_current_metrics()
        alerts = self.check_alerts()
        
        report_lines = [
            "=" * 80,
            "DATA QUALITY MONITORING REPORT",
            "=" * 80,
            "",
            f"Generated: {metrics['timestamp']}",
            "",
        ]
        
        # Seção de Estatísticas
        report_lines.extend([
            "📊 COLLECTION STATISTICS",
            "-" * 80,
        ])
        
        for collection_name, stats in metrics["statistics"]["collections"].items():
            report_lines.append(f"\n{collection_name}:")
            report_lines.append(f"  Records: {stats['count']}")
            report_lines.append(f"  Oldest: {stats['oldest_record'] or 'N/A'}")
            report_lines.append(f"  Newest: {stats['newest_record'] or 'N/A'}")
        
        # Seção de Qualidade
        report_lines.extend([
            "",
            "✅ QUALITY METRICS",
            "-" * 80,
        ])
        
        quality = metrics["quality"]
        report_lines.append(f"Overall Quality Score: {quality['overall_quality_score']:.2%}")
        report_lines.append(f"Valid Records: {quality['total_valid_records']}")
        report_lines.append(f"Invalid Records: {quality['total_invalid_records']}")
        
        if "quality" in quality and "valid" in quality["quality"]:
            report_lines.append("\nValid by type:")
            for dtype, count in quality["quality"]["valid"].items():
                if isinstance(count, int):
                    report_lines.append(f"  - {dtype}: {count}")
        
        # Seção de Sincronização
        if "synchronization" in metrics and "metrics" in metrics["synchronization"]:
            report_lines.extend([
                "",
                "🔄 SYNCHRONIZATION STATUS",
                "-" * 80,
            ])
            
            sync_metrics = metrics["synchronization"]["metrics"]
            for collection_name, sync_data in sync_metrics.items():
                report_lines.append(f"\n{collection_name}:")
                report_lines.append(f"  Status: {sync_data['status']}")
                report_lines.append(f"  Records Synced: {sync_data['records_synced']}")
                report_lines.append(f"  Duration: {sync_data['duration_seconds']:.1f}s")
        
        # Seção de Alertas
        report_lines.extend([
            "",
            "⚠️  ALERTS",
            "-" * 80,
        ])
        
        if alerts:
            for alert in alerts:
                severity = alert["severity"]
                message = alert["message"]
                report_lines.append(f"[{severity}] {message}")
        else:
            report_lines.append("No alerts - all systems nominal ✓")
        
        # Resumo
        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80,
        ])
        
        return "\n".join(report_lines)
    
    def get_dashboard_summary(self) -> Dict:
        """
        Retorna sumário para dashboards visuais.
        
        Returns:
            Dict com dados resumidos
        """
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest = self.metrics_history[-1]
        alerts = self.check_alerts()
        
        # Calcular tendências
        quality_trend = []
        if len(self.metrics_history) >= 2:
            for metric in self.metrics_history[-10:]:  # Últimas 10 medições
                score = metric["quality"].get("overall_quality_score", 0)
                quality_trend.append(score)
        
        return {
            "status": "healthy" if not alerts else "warning",
            "timestamp": latest["timestamp"],
            "quality_score": latest["quality"].get("overall_quality_score", 0),
            "quality_trend": quality_trend,
            "total_records": sum(
                stats["count"]
                for stats in latest["statistics"]["collections"].values()
            ),
            "alerts_count": len(alerts),
            "critical_alerts": len([a for a in alerts if a["severity"] == "CRITICAL"]),
            "warnings": len([a for a in alerts if a["severity"] == "WARNING"]),
            "collections": {
                name: stats["count"]
                for name, stats in latest["statistics"]["collections"].items()
            },
        }
    
    def export_metrics(self, filepath: str):
        """
        Exporta métricas para arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo de exportação
        """
        try:
            data = {
                "export_time": datetime.now().isoformat(),
                "metrics_count": len(self.metrics_history),
                "alerts_count": len(self.alert_history),
                "metrics": self.metrics_history[-100:],  # Últimas 100
                "alerts": self.alert_history[-100:],     # Últimos 100
            }
            
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Exported metrics to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
