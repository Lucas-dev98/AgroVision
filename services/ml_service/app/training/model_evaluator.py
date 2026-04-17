"""
Model Evaluation Framework - Avalia modelos com métricas especializadas

Responsabilidades:
- Métricas por classe
- Confusion matrix
- ROC-AUC, Precision-Recall
- Métricas de comportamento
- Comparação entre modelos
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

import torch
import torch.nn as nn
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_auc_score,
    precision_recall_curve, f1_score, accuracy_score,
)


logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Métricas gerais de modelo"""
    accuracy: float
    precision: float
    recall: float
    f1: float
    loss: float


@dataclass
class ClassMetrics:
    """Métricas por classe"""
    class_name: str
    precision: float
    recall: float
    f1: float
    support: int


@dataclass
class BehaviorMetrics:
    """Métricas especializadas para comportamento"""
    behavior_class: str
    detection_rate: float  # True positives / positives
    false_positive_rate: float
    confusion_with_classes: Dict[str, float]  # Quais classes confunde mais


class ModelEvaluator:
    """
    Framework para avaliação completa de modelos.
    
    Calcula:
    - Métricas gerais (accuracy, precision, recall, F1)
    - Métricas por classe
    - Confusion matrix
    - ROC-AUC
    - Análise de erros
    - Comparação entre modelos
    
    Exemplo:
        ```python
        evaluator = ModelEvaluator(model, device="cuda")
        
        # Avaliar modelo
        metrics = await evaluator.evaluate(
            val_loader=val_loader,
            loss_fn=loss_fn,
            class_names=["grazing", "walking", "resting", "drinking", "eating", "standing", "running", "lying"],
        )
        
        # Gerar relatório
        report = evaluator.generate_report()
        print(report)
        
        # Análise de erros
        error_analysis = evaluator.analyze_errors()
        ```
    """
    
    def __init__(
        self,
        model: nn.Module,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        """
        Inicializa o evaluator.
        
        Args:
            model: Modelo PyTorch
            device: Dispositivo (cuda/cpu)
        """
        self.model = model
        self.device = device
        
        self.predictions: List[int] = []
        self.targets: List[int] = []
        self.probabilities: List[np.ndarray] = []
        self.losses: List[float] = []
        
        self.metrics: Optional[ModelMetrics] = None
        self.class_metrics: Dict[int, ClassMetrics] = {}
        self.confusion_matrix: Optional[np.ndarray] = None
        self.class_names: List[str] = []
    
    async def evaluate(
        self,
        val_loader,
        loss_fn: nn.Module,
        class_names: Optional[List[str]] = None,
    ) -> ModelMetrics:
        """
        Avalia modelo nos dados de validação.
        
        Args:
            val_loader: DataLoader de validação
            loss_fn: Função de loss
            class_names: Nomes das classes (para relatórios)
            
        Returns:
            ModelMetrics com resultados
        """
        self.class_names = class_names or []
        self.predictions = []
        self.targets = []
        self.probabilities = []
        self.losses = []
        
        logger.info("Starting model evaluation...")
        
        self.model.eval()
        
        with torch.no_grad():
            for batch in val_loader:
                x, y = batch
                x = x.to(self.device)
                y = y.to(self.device)
                
                # Forward pass
                outputs = self.model(x)
                loss = loss_fn(outputs, y)
                
                # Get predictions
                if outputs.dim() > 1 and outputs.size(1) > 1:
                    # Classification: softmax
                    probs = torch.softmax(outputs, dim=1)
                    preds = torch.argmax(outputs, dim=1)
                else:
                    # Binary or regression
                    probs = torch.sigmoid(outputs)
                    preds = (probs > 0.5).long().squeeze()
                
                # Record
                self.predictions.extend(preds.cpu().numpy().tolist())
                self.targets.extend(y.cpu().numpy().tolist())
                self.probabilities.extend(probs.cpu().numpy())
                self.losses.append(loss.item())
        
        # Calcular métricas
        self._compute_metrics()
        
        logger.info(f"Evaluation complete: Accuracy={self.metrics.accuracy:.4f}")
        
        return self.metrics
    
    def _compute_metrics(self):
        """Calcula métricas gerais."""
        predictions = np.array(self.predictions)
        targets = np.array(self.targets)
        
        accuracy = accuracy_score(targets, predictions)
        f1 = f1_score(targets, predictions, average="weighted", zero_division=0)
        
        # Precision e Recall
        from sklearn.metrics import precision_score, recall_score
        precision = precision_score(targets, predictions, average="weighted", zero_division=0)
        recall = recall_score(targets, predictions, average="weighted", zero_division=0)
        
        avg_loss = np.mean(self.losses)
        
        self.metrics = ModelMetrics(
            accuracy=float(accuracy),
            precision=float(precision),
            recall=float(recall),
            f1=float(f1),
            loss=float(avg_loss),
        )
        
        # Confusion matrix
        self.confusion_matrix = confusion_matrix(targets, predictions)
        
        # Métricas por classe
        report = classification_report(
            targets,
            predictions,
            output_dict=True,
            zero_division=0,
        )
        
        for class_idx in range(self.confusion_matrix.shape[0]):
            if class_idx < len(self.class_names):
                class_name = self.class_names[class_idx]
            else:
                class_name = f"class_{class_idx}"
            
            if str(class_idx) in report:
                class_report = report[str(class_idx)]
                self.class_metrics[class_idx] = ClassMetrics(
                    class_name=class_name,
                    precision=float(class_report["precision"]),
                    recall=float(class_report["recall"]),
                    f1=float(class_report["f1-score"]),
                    support=int(class_report["support"]),
                )
    
    def analyze_errors(self) -> Dict:
        """
        Analisa erros do modelo.
        
        Returns:
            Dict com análise de erros
        """
        predictions = np.array(self.predictions)
        targets = np.array(self.targets)
        
        # Encontrar erros
        errors = predictions != targets
        error_indices = np.where(errors)[0]
        
        # Contar erros por classe
        error_counts = {}
        for true_class in np.unique(targets):
            class_mask = targets == true_class
            class_errors = np.sum(errors[class_mask])
            total_class = np.sum(class_mask)
            
            error_counts[f"class_{true_class}"] = {
                "true_positive_errors": int(class_errors),
                "total": int(total_class),
                "error_rate": float(class_errors / total_class) if total_class > 0 else 0.0,
            }
        
        # Pares de confusão mais frequentes
        confusion_pairs = {}
        for error_idx in error_indices[:100]:  # Primeiros 100 erros
            true_class = targets[error_idx]
            pred_class = predictions[error_idx]
            key = f"{true_class} -> {pred_class}"
            
            confusion_pairs[key] = confusion_pairs.get(key, 0) + 1
        
        # Ordenar por frequência
        confusion_pairs = dict(sorted(
            confusion_pairs.items(),
            key=lambda x: x[1],
            reverse=True,
        ))
        
        return {
            "total_errors": int(np.sum(errors)),
            "error_rate": float(np.sum(errors) / len(targets)),
            "errors_by_class": error_counts,
            "top_confusion_pairs": dict(list(confusion_pairs.items())[:10]),
        }
    
    def get_class_metrics(self, class_name: str) -> Optional[ClassMetrics]:
        """Obtém métricas de uma classe específica."""
        for class_idx, metrics in self.class_metrics.items():
            if metrics.class_name == class_name:
                return metrics
        return None
    
    def generate_report(self) -> str:
        """Gera relatório de avaliação em formato de texto."""
        lines = [
            "=" * 80,
            "MODEL EVALUATION REPORT",
            "=" * 80,
            "",
        ]
        
        # Seção de Métricas Gerais
        lines.extend([
            "📊 OVERALL METRICS",
            "-" * 80,
            f"Accuracy:  {self.metrics.accuracy:.4f}",
            f"Precision: {self.metrics.precision:.4f}",
            f"Recall:    {self.metrics.recall:.4f}",
            f"F1 Score:  {self.metrics.f1:.4f}",
            f"Loss:      {self.metrics.loss:.4f}",
            "",
        ])
        
        # Seção de Métricas por Classe
        lines.extend([
            "📋 PER-CLASS METRICS",
            "-" * 80,
        ])
        
        for class_idx, metrics in sorted(self.class_metrics.items()):
            lines.append(
                f"{metrics.class_name:20s} | "
                f"P: {metrics.precision:.4f} | "
                f"R: {metrics.recall:.4f} | "
                f"F1: {metrics.f1:.4f} | "
                f"Support: {metrics.support}"
            )
        
        lines.append("")
        
        # Seção de Análise de Erros
        error_analysis = self.analyze_errors()
        lines.extend([
            "❌ ERROR ANALYSIS",
            "-" * 80,
            f"Total Errors:  {error_analysis['total_errors']}",
            f"Error Rate:    {error_analysis['error_rate']:.4f}",
            "",
            "Top Confusion Pairs:",
        ])
        
        for pair, count in list(error_analysis["top_confusion_pairs"].items())[:5]:
            lines.append(f"  {pair}: {count}")
        
        lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80,
        ])
        
        return "\n".join(lines)
    
    def get_confusion_matrix_summary(self) -> Dict:
        """Retorna sumário da confusion matrix."""
        if self.confusion_matrix is None:
            return {}
        
        summary = {
            "shape": self.confusion_matrix.shape,
            "true_positives": [],
            "false_positives": [],
            "false_negatives": [],
            "true_negatives": [],
        }
        
        for i in range(self.confusion_matrix.shape[0]):
            # True positives: diagonal
            summary["true_positives"].append(int(self.confusion_matrix[i, i]))
            
            # False positives: coluna (predições incorretas)
            summary["false_positives"].append(int(np.sum(self.confusion_matrix[:, i]) - self.confusion_matrix[i, i]))
            
            # False negatives: linha (não detectados)
            summary["false_negatives"].append(int(np.sum(self.confusion_matrix[i, :]) - self.confusion_matrix[i, i]))
        
        return summary
    
    def compare_with_baseline(self, baseline_metrics: ModelMetrics) -> Dict:
        """
        Compara com baseline.
        
        Args:
            baseline_metrics: Métricas de baseline
            
        Returns:
            Dict com comparação
        """
        return {
            "accuracy_diff": self.metrics.accuracy - baseline_metrics.accuracy,
            "accuracy_improvement_pct": ((self.metrics.accuracy - baseline_metrics.accuracy) / baseline_metrics.accuracy * 100) if baseline_metrics.accuracy > 0 else 0,
            "precision_diff": self.metrics.precision - baseline_metrics.precision,
            "recall_diff": self.metrics.recall - baseline_metrics.recall,
            "f1_diff": self.metrics.f1 - baseline_metrics.f1,
            "loss_diff": self.metrics.loss - baseline_metrics.loss,
        }
