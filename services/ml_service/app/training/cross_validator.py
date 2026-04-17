"""
Cross-Validation Framework - Valida modelos com múltiplas estratégias

Responsabilidades:
- K-fold cross-validation
- Stratified K-fold
- Time-series cross-validation
- Hold-out validation
- Métricas de estabilidade de modelo
"""

import logging
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
import numpy as np

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset


logger = logging.getLogger(__name__)


@dataclass
class CrossValidationMetrics:
    """Métricas de cross-validation"""
    fold_losses: List[float]
    fold_accuracies: List[float]
    mean_loss: float
    std_loss: float
    mean_accuracy: float
    std_accuracy: float
    variance_coefficient: float  # std / mean - medida de estabilidade


class CrossValidator:
    """
    Framework de cross-validation para validação robusta de modelos.
    
    Estratégias suportadas:
    - K-Fold: Divisão aleatória em K partes
    - Stratified K-Fold: Mantém distribuição de classes
    - Time-Series K-Fold: Respeitsa temporalidade dos dados
    - Hold-Out: Train/Val/Test simples
    
    Exemplo:
        ```python
        validator = CrossValidator(model, device="cuda")
        
        # 5-fold cross-validation
        metrics = await validator.kfold_cross_validate(
            dataset=dataset,
            k=5,
            batch_size=32,
            epochs=10,
        )
        
        print(f"Mean Accuracy: {metrics.mean_accuracy:.4f} ± {metrics.std_accuracy:.4f}")
        ```
    """
    
    def __init__(
        self,
        model_class: type,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        """
        Inicializa o cross-validator.
        
        Args:
            model_class: Classe do modelo (para criar novas instâncias)
            device: Dispositivo (cuda/cpu)
        """
        self.model_class = model_class
        self.device = device
    
    async def kfold_cross_validate(
        self,
        dataset,
        k: int = 5,
        batch_size: int = 32,
        epochs: int = 10,
        loss_fn: Optional[nn.Module] = None,
        train_step_fn: Optional[Callable] = None,
        val_step_fn: Optional[Callable] = None,
        seed: int = 42,
    ) -> CrossValidationMetrics:
        """
        Executa K-fold cross-validation.
        
        Args:
            dataset: Dataset PyTorch
            k: Número de folds
            batch_size: Tamanho do batch
            epochs: Épocas por fold
            loss_fn: Função de loss
            train_step_fn: Função customizada de treinamento
            val_step_fn: Função customizada de validação
            seed: Random seed para reproducibilidade
            
        Returns:
            CrossValidationMetrics com resultados
        """
        logger.info(f"Starting {k}-fold cross-validation")
        
        np.random.seed(seed)
        torch.manual_seed(seed)
        
        fold_losses = []
        fold_accuracies = []
        
        # Criar índices para folds
        indices = np.arange(len(dataset))
        np.random.shuffle(indices)
        fold_size = len(dataset) // k
        
        for fold_idx in range(k):
            logger.info(f"Fold {fold_idx + 1}/{k}")
            
            # Dividir dados
            val_start = fold_idx * fold_size
            val_end = val_start + fold_size if fold_idx < k - 1 else len(dataset)
            
            val_indices = indices[val_start:val_end]
            train_indices = np.concatenate([indices[:val_start], indices[val_end:]])
            
            # Criar subsets
            train_subset = Subset(dataset, train_indices)
            val_subset = Subset(dataset, val_indices)
            
            # Criar dataloaders
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False)
            
            # Criar novo modelo
            model = self.model_class()
            model.to(self.device)
            
            # Treinar
            val_loss, val_accuracy = await self._train_and_evaluate(
                model=model,
                train_loader=train_loader,
                val_loader=val_loader,
                epochs=epochs,
                loss_fn=loss_fn,
                train_step_fn=train_step_fn,
                val_step_fn=val_step_fn,
            )
            
            fold_losses.append(val_loss)
            fold_accuracies.append(val_accuracy)
            
            logger.info(f"Fold {fold_idx + 1} - Loss: {val_loss:.4f}, Accuracy: {val_accuracy:.4f}")
        
        # Calcular métricas
        metrics = self._compute_metrics(fold_losses, fold_accuracies)
        
        logger.info(f"Cross-validation complete: {metrics.mean_accuracy:.4f} ± {metrics.std_accuracy:.4f}")
        
        return metrics
    
    async def stratified_kfold_cross_validate(
        self,
        dataset,
        labels,
        k: int = 5,
        batch_size: int = 32,
        epochs: int = 10,
        loss_fn: Optional[nn.Module] = None,
        train_step_fn: Optional[Callable] = None,
        val_step_fn: Optional[Callable] = None,
        seed: int = 42,
    ) -> CrossValidationMetrics:
        """
        Executa Stratified K-fold cross-validation.
        
        Mantém a distribuição de classes em cada fold.
        
        Args:
            dataset: Dataset PyTorch
            labels: Array de labels para stratificação
            k: Número de folds
            batch_size: Tamanho do batch
            epochs: Épocas por fold
            loss_fn: Função de loss
            train_step_fn: Função customizada de treinamento
            val_step_fn: Função customizada de validação
            seed: Random seed
            
        Returns:
            CrossValidationMetrics com resultados
        """
        logger.info(f"Starting Stratified {k}-fold cross-validation")
        
        from sklearn.model_selection import StratifiedKFold
        
        np.random.seed(seed)
        torch.manual_seed(seed)
        
        fold_losses = []
        fold_accuracies = []
        
        skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=seed)
        labels_array = np.array(labels)
        
        fold_idx = 0
        for train_indices, val_indices in skf.split(np.arange(len(dataset)), labels_array):
            logger.info(f"Fold {fold_idx + 1}/{k}")
            
            # Criar subsets
            train_subset = Subset(dataset, train_indices)
            val_subset = Subset(dataset, val_indices)
            
            # Criar dataloaders
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False)
            
            # Criar novo modelo
            model = self.model_class()
            model.to(self.device)
            
            # Treinar
            val_loss, val_accuracy = await self._train_and_evaluate(
                model=model,
                train_loader=train_loader,
                val_loader=val_loader,
                epochs=epochs,
                loss_fn=loss_fn,
                train_step_fn=train_step_fn,
                val_step_fn=val_step_fn,
            )
            
            fold_losses.append(val_loss)
            fold_accuracies.append(val_accuracy)
            
            logger.info(f"Fold {fold_idx + 1} - Loss: {val_loss:.4f}, Accuracy: {val_accuracy:.4f}")
            fold_idx += 1
        
        # Calcular métricas
        metrics = self._compute_metrics(fold_losses, fold_accuracies)
        
        logger.info(f"Stratified cross-validation complete: {metrics.mean_accuracy:.4f} ± {metrics.std_accuracy:.4f}")
        
        return metrics
    
    async def timeseries_kfold_cross_validate(
        self,
        dataset,
        k: int = 5,
        batch_size: int = 32,
        epochs: int = 10,
        loss_fn: Optional[nn.Module] = None,
        train_step_fn: Optional[Callable] = None,
        val_step_fn: Optional[Callable] = None,
    ) -> CrossValidationMetrics:
        """
        Executa Time-Series K-fold cross-validation.
        
        Respeita ordem temporal dos dados (importante para dados sequenciais).
        Sempre treina em dados anteriores, valida em dados posteriores.
        
        Args:
            dataset: Dataset PyTorch com dados em ordem temporal
            k: Número de folds
            batch_size: Tamanho do batch
            epochs: Épocas por fold
            loss_fn: Função de loss
            train_step_fn: Função customizada de treinamento
            val_step_fn: Função customizada de validação
            
        Returns:
            CrossValidationMetrics com resultados
        """
        logger.info(f"Starting Time-Series {k}-fold cross-validation")
        
        fold_losses = []
        fold_accuracies = []
        
        total_size = len(dataset)
        fold_size = total_size // (k + 1)
        
        for fold_idx in range(k):
            logger.info(f"Fold {fold_idx + 1}/{k}")
            
            # Time-series split: train em dados antigos, val em dados novos
            train_end = (fold_idx + 1) * fold_size
            val_start = train_end
            val_end = val_start + fold_size
            
            train_indices = np.arange(0, train_end)
            val_indices = np.arange(val_start, min(val_end, total_size))
            
            # Criar subsets
            train_subset = Subset(dataset, train_indices)
            val_subset = Subset(dataset, val_indices)
            
            # Criar dataloaders
            train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
            val_loader = DataLoader(val_subset, batch_size=batch_size, shuffle=False)
            
            # Criar novo modelo
            model = self.model_class()
            model.to(self.device)
            
            # Treinar
            val_loss, val_accuracy = await self._train_and_evaluate(
                model=model,
                train_loader=train_loader,
                val_loader=val_loader,
                epochs=epochs,
                loss_fn=loss_fn,
                train_step_fn=train_step_fn,
                val_step_fn=val_step_fn,
            )
            
            fold_losses.append(val_loss)
            fold_accuracies.append(val_accuracy)
            
            logger.info(f"Fold {fold_idx + 1} - Loss: {val_loss:.4f}, Accuracy: {val_accuracy:.4f}")
        
        # Calcular métricas
        metrics = self._compute_metrics(fold_losses, fold_accuracies)
        
        logger.info(f"Time-series cross-validation complete: {metrics.mean_accuracy:.4f} ± {metrics.std_accuracy:.4f}")
        
        return metrics
    
    async def _train_and_evaluate(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int,
        loss_fn: Optional[nn.Module],
        train_step_fn: Optional[Callable],
        val_step_fn: Optional[Callable],
    ) -> Tuple[float, float]:
        """Treina e avalia modelo em um fold."""
        import torch.optim as optim
        
        loss_fn = loss_fn or nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        for epoch in range(epochs):
            # Train
            model.train()
            for batch in train_loader:
                optimizer.zero_grad()
                
                if train_step_fn:
                    loss = await train_step_fn(model, batch, self.device, loss_fn)
                else:
                    x, y = batch
                    x = x.to(self.device)
                    y = y.to(self.device)
                    
                    outputs = model(x)
                    loss = loss_fn(outputs, y)
                
                loss.backward()
                optimizer.step()
            
            # Validate
            model.eval()
            total_loss = 0.0
            correct = 0
            total = 0
            
            with torch.no_grad():
                for batch in val_loader:
                    if val_step_fn:
                        loss, acc = await val_step_fn(model, batch, self.device, loss_fn)
                        total_loss += loss
                        correct += acc
                        total += 1
                    else:
                        x, y = batch
                        x = x.to(self.device)
                        y = y.to(self.device)
                        
                        outputs = model(x)
                        loss = loss_fn(outputs, y)
                        
                        total_loss += loss.item()
                        _, predicted = torch.max(outputs.data, 1)
                        correct += (predicted == y).sum().item()
                        total += y.size(0)
        
        avg_loss = total_loss / len(val_loader) if len(val_loader) > 0 else 0.0
        accuracy = correct / total if total > 0 else 0.0
        
        return avg_loss, accuracy
    
    def _compute_metrics(
        self,
        fold_losses: List[float],
        fold_accuracies: List[float],
    ) -> CrossValidationMetrics:
        """Calcula métricas de CV."""
        fold_losses = np.array(fold_losses)
        fold_accuracies = np.array(fold_accuracies)
        
        mean_loss = float(np.mean(fold_losses))
        std_loss = float(np.std(fold_losses))
        mean_accuracy = float(np.mean(fold_accuracies))
        std_accuracy = float(np.std(fold_accuracies))
        
        # Coeficiente de variação (estabilidade)
        variance_coefficient = std_accuracy / (mean_accuracy + 1e-10)
        
        return CrossValidationMetrics(
            fold_losses=fold_losses.tolist(),
            fold_accuracies=fold_accuracies.tolist(),
            mean_loss=mean_loss,
            std_loss=std_loss,
            mean_accuracy=mean_accuracy,
            std_accuracy=std_accuracy,
            variance_coefficient=variance_coefficient,
        )
