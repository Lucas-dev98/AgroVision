"""Model metrics and evaluation functions"""

import numpy as np
from typing import Dict, Tuple, List
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    mean_squared_error,
    mean_absolute_error,
)


class ClassificationMetrics:
    """Metrics for classification tasks"""

    @staticmethod
    def calculate_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        average: str = "weighted",
    ) -> Dict[str, float]:
        """
        Calculate classification metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            average: Averaging method ('weighted', 'macro', 'micro')
            
        Returns:
            Dictionary of metrics
        """
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
        }

    @staticmethod
    def get_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Get confusion matrix"""
        return confusion_matrix(y_true, y_pred)

    @staticmethod
    def print_metrics(metrics: Dict[str, float]):
        """Pretty print metrics"""
        print("\n📊 Classification Metrics:")
        for metric_name, value in metrics.items():
            print(f"   {metric_name.capitalize():12} {value:.4f}")


class AnomalyMetrics:
    """Metrics for anomaly detection"""

    @staticmethod
    def calculate_reconstruction_error(
        original: np.ndarray,
        reconstructed: np.ndarray,
    ) -> float:
        """
        Calculate reconstruction error (MSE)
        
        Args:
            original: Original features
            reconstructed: Reconstructed features
            
        Returns:
            MSE error
        """
        return float(mean_squared_error(original, reconstructed))

    @staticmethod
    def calculate_reconstruction_errors_batch(
        originals: np.ndarray,
        reconstructeds: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate reconstruction error for batch
        
        Args:
            originals: (N, D) original features
            reconstructeds: (N, D) reconstructed features
            
        Returns:
            (N,) array of per-sample errors
        """
        return np.mean((originals - reconstructeds) ** 2, axis=1)

    @staticmethod
    def get_optimal_threshold(
        normal_errors: np.ndarray,
        anomaly_errors: np.ndarray,
    ) -> float:
        """
        Get optimal threshold using ROC curve
        
        Args:
            normal_errors: Errors from normal samples
            anomaly_errors: Errors from anomalous samples
            
        Returns:
            Optimal threshold
        """
        all_errors = np.concatenate([normal_errors, anomaly_errors])
        all_labels = np.concatenate([
            np.zeros(len(normal_errors)),
            np.ones(len(anomaly_errors)),
        ])

        # Threshold at mean of anomaly errors
        threshold = np.mean(anomaly_errors) * 1.2

        return float(threshold)

    @staticmethod
    def evaluate_anomaly_detection(
        true_labels: np.ndarray,
        pred_labels: np.ndarray,
    ) -> Dict[str, float]:
        """
        Evaluate anomaly detection
        
        Args:
            true_labels: True anomaly labels (0=normal, 1=anomaly)
            pred_labels: Predicted labels
            
        Returns:
            Dictionary of metrics
        """
        return {
            "accuracy": float(accuracy_score(true_labels, pred_labels)),
            "precision": float(precision_score(true_labels, pred_labels, zero_division=0)),
            "recall": float(recall_score(true_labels, pred_labels, zero_division=0)),
            "f1": float(f1_score(true_labels, pred_labels, zero_division=0)),
        }

    @staticmethod
    def print_anomaly_metrics(metrics: Dict[str, float]):
        """Pretty print anomaly metrics"""
        print("\n🔍 Anomaly Detection Metrics:")
        for metric_name, value in metrics.items():
            print(f"   {metric_name.capitalize():12} {value:.4f}")


class ReIDMetrics:
    """Metrics for Re-identification"""

    @staticmethod
    def calculate_similarity(
        features1: np.ndarray,
        features2: np.ndarray,
    ) -> float:
        """
        Calculate cosine similarity between features
        
        Args:
            features1: (D,) feature vector 1
            features2: (D,) feature vector 2
            
        Returns:
            Cosine similarity
        """
        # Normalize
        f1 = features1 / (np.linalg.norm(features1) + 1e-8)
        f2 = features2 / (np.linalg.norm(features2) + 1e-8)

        return float(np.dot(f1, f2))

    @staticmethod
    def calculate_similarity_matrix(features_list: List[np.ndarray]) -> np.ndarray:
        """
        Calculate pairwise similarity matrix
        
        Args:
            features_list: List of (D,) feature vectors
            
        Returns:
            (N, N) similarity matrix
        """
        n = len(features_list)
        similarities = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                similarities[i, j] = ReIDMetrics.calculate_similarity(
                    features_list[i],
                    features_list[j],
                )

        return similarities

    @staticmethod
    def get_rank_metrics(
        similarity_matrix: np.ndarray,
        true_labels: np.ndarray,
    ) -> Dict[str, float]:
        """
        Calculate rank-based metrics (CMC curve)
        
        Args:
            similarity_matrix: (N, N) pairwise similarities
            true_labels: (N,) true identity labels
            
        Returns:
            Rank-1, Rank-5, mAP metrics
        """
        n = len(true_labels)
        rank1_correct = 0
        rank5_correct = 0
        ap_list = []

        for i in range(n):
            # Get rankings
            rankings = np.argsort(similarity_matrix[i])[::-1]

            # Remove self
            rankings = rankings[rankings != i]

            # Rank-1
            if true_labels[rankings[0]] == true_labels[i]:
                rank1_correct += 1

            # Rank-5
            if len(rankings) >= 5:
                rank5_mask = np.isin(rankings[:5], np.where(true_labels == true_labels[i])[0])
                if np.any(rank5_mask):
                    rank5_correct += 1

            # Average precision
            if len(rankings) > 0:
                matches = true_labels[rankings] == true_labels[i]
                if np.any(matches):
                    precisions = np.cumsum(matches) / (np.arange(len(matches)) + 1)
                    ap = np.mean(precisions[matches])
                    ap_list.append(ap)

        return {
            "rank1_accuracy": float(rank1_correct / n),
            "rank5_accuracy": float(rank5_correct / n),
            "mean_ap": float(np.mean(ap_list)) if ap_list else 0.0,
        }

    @staticmethod
    def print_reid_metrics(metrics: Dict[str, float]):
        """Pretty print Re-ID metrics"""
        print("\n🎯 Re-Identification Metrics:")
        for metric_name, value in metrics.items():
            print(f"   {metric_name.capitalize():20} {value:.4f}")


class TemporalMetrics:
    """Metrics for temporal models"""

    @staticmethod
    def calculate_sequence_accuracy(
        y_true_sequences: List[np.ndarray],
        y_pred_sequences: List[np.ndarray],
    ) -> float:
        """
        Calculate accuracy on sequences
        
        Args:
            y_true_sequences: List of true labels per sequence
            y_pred_sequences: List of predicted labels per sequence
            
        Returns:
            Accuracy
        """
        all_true = np.concatenate(y_true_sequences)
        all_pred = np.concatenate(y_pred_sequences)

        return float(accuracy_score(all_true, all_pred))

    @staticmethod
    def calculate_temporal_consistency(
        y_pred_sequences: List[np.ndarray],
    ) -> float:
        """
        Calculate temporal consistency (smoothness)
        Higher is better (fewer label changes)
        
        Args:
            y_pred_sequences: List of predicted labels per sequence
            
        Returns:
            Consistency score (0-1)
        """
        total_changes = 0
        total_transitions = 0

        for seq in y_pred_sequences:
            if len(seq) > 1:
                changes = np.sum(np.diff(seq) != 0)
                total_changes += changes
                total_transitions += len(seq) - 1

        if total_transitions == 0:
            return 1.0

        consistency = 1.0 - (total_changes / total_transitions)
        return float(consistency)

    @staticmethod
    def print_temporal_metrics(metrics: Dict[str, float]):
        """Pretty print temporal metrics"""
        print("\n⏱️  Temporal Metrics:")
        for metric_name, value in metrics.items():
            print(f"   {metric_name.capitalize():20} {value:.4f}")


class ModelEvaluator:
    """Unified model evaluation"""

    @staticmethod
    def evaluate_classification_model(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray = None,
    ) -> Dict:
        """Evaluate classification model"""
        metrics = ClassificationMetrics.calculate_metrics(y_true, y_pred)

        if y_pred_proba is not None and len(np.unique(y_true)) == 2:
            try:
                metrics["roc_auc"] = float(roc_auc_score(y_true, y_pred_proba[:, 1]))
            except:
                pass

        return metrics

    @staticmethod
    def evaluate_anomaly_model(
        normal_errors: np.ndarray,
        anomaly_errors: np.ndarray,
    ) -> Dict:
        """Evaluate anomaly detection model"""
        threshold = AnomalyMetrics.get_optimal_threshold(normal_errors, anomaly_errors)

        pred_labels = np.concatenate([
            (normal_errors > threshold).astype(int),
            (anomaly_errors > threshold).astype(int),
        ])

        true_labels = np.concatenate([
            np.zeros(len(normal_errors), dtype=int),
            np.ones(len(anomaly_errors), dtype=int),
        ])

        return AnomalyMetrics.evaluate_anomaly_detection(true_labels, pred_labels)

    @staticmethod
    def evaluate_reid_model(
        features_same_identity: List[Tuple[np.ndarray, np.ndarray]],
        features_different_identity: List[Tuple[np.ndarray, np.ndarray]],
    ) -> Dict:
        """Evaluate Re-ID model"""
        # Calculate similarities
        same_similarities = [
            ReIDMetrics.calculate_similarity(f1, f2)
            for f1, f2 in features_same_identity
        ]

        diff_similarities = [
            ReIDMetrics.calculate_similarity(f1, f2)
            for f1, f2 in features_different_identity
        ]

        # ROC AUC
        true_labels = np.concatenate([
            np.ones(len(same_similarities)),
            np.zeros(len(diff_similarities)),
        ])

        pred_scores = np.concatenate([same_similarities, diff_similarities])

        roc_auc = roc_auc_score(true_labels, pred_scores)

        # Find optimal threshold
        thresholds = np.linspace(0, 1, 100)
        best_threshold = 0.5
        best_f1 = 0

        for threshold in thresholds:
            pred_labels = (pred_scores >= threshold).astype(int)
            f1 = f1_score(true_labels, pred_labels)

            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

        return {
            "roc_auc": float(roc_auc),
            "optimal_threshold": float(best_threshold),
            "f1_at_threshold": float(best_f1),
        }

    @staticmethod
    def print_summary(model_name: str, metrics: Dict):
        """Print evaluation summary"""
        print("\n" + "=" * 50)
        print(f"📈 {model_name} Evaluation Summary")
        print("=" * 50)

        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key:20} {value:.4f}")
            else:
                print(f"  {key:20} {value}")
