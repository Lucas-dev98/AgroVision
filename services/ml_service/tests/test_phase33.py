"""
Tests for FASE 3.3 - Model Fine-tuning & Evaluation

Testa:
- Fine-tuning framework
- Cross-validation system
- Model evaluation
- Hyperparameter optimization
"""

import pytest
import asyncio
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader, TensorDataset

from app.training.finetuner import FinetuneLearner, FinetuneConfig
from app.training.cross_validator import CrossValidator, CrossValidationMetrics
from app.training.model_evaluator import ModelEvaluator


# Simple test model
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
        )
        self.head = nn.Linear(20, 2)
    
    def forward(self, x):
        x = self.backbone(x)
        x = self.head(x)
        return x


# ============================================================================
# Tests for FinetuneLearner
# ============================================================================

class TestFinetuneLearner:
    """Testes para o framework de fine-tuning."""
    
    def test_init(self):
        """Verifica se inicializa corretamente."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        
        assert learner.model == model
        assert learner.device == "cpu"
        assert len(learner.results["train_losses"]) == 0
    
    def test_freeze_backbone(self):
        """Verifica se congela backbone corretamente."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        learner._freeze_backbone()
        
        # Verificar que backbone está congelado
        for name, param in model.named_parameters():
            if "backbone" in name:
                assert not param.requires_grad
    
    def test_unfreeze_all(self):
        """Verifica se descongela todos os pesos."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        learner._freeze_backbone()
        learner._unfreeze_all()
        
        # Todos devem estar descongelados
        for param in model.parameters():
            assert param.requires_grad
    
    def test_get_discriminative_lr_groups(self):
        """Verifica se cria grupos de LR discriminativos."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        groups = learner.get_discriminative_lr_groups(base_lr=0.001)
        
        assert len(groups) > 0
        assert "params" in groups[0]
        assert "lr" in groups[0]
    
    def test_setup_optimizer_adamw(self):
        """Verifica se configura otimizador AdamW."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        config = FinetuneConfig(learning_rate=0.001)
        
        learner.setup_optimizer(config, optimizer_type="adamw")
        
        assert learner.optimizer is not None
        assert isinstance(learner.optimizer, torch.optim.AdamW)
    
    def test_setup_optimizer_sgd(self):
        """Verifica se configura otimizador SGD."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        config = FinetuneConfig(learning_rate=0.001)
        
        learner.setup_optimizer(config, optimizer_type="sgd")
        
        assert learner.optimizer is not None
        assert isinstance(learner.optimizer, torch.optim.SGD)
    
    def test_generate_summary(self):
        """Verifica se gera sumário corretamente."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        learner.results["train_losses"] = [0.5, 0.4, 0.3]
        learner.results["val_losses"] = [0.5, 0.4, 0.3]
        learner.results["val_accuracies"] = [0.8, 0.85, 0.9]
        learner.results["best_val_loss"] = 0.3
        learner.results["best_val_accuracy"] = 0.9
        learner.results["best_epoch"] = 2
        
        learner._generate_summary()
        
        summary = learner.results["summary"]
        assert summary["total_epochs_trained"] == 3
        assert summary["best_epoch"] == 2
        assert summary["best_val_accuracy"] == 0.9


# ============================================================================
# Tests for CrossValidator
# ============================================================================

class TestCrossValidator:
    """Testes para cross-validation."""
    
    def test_init(self):
        """Verifica se inicializa corretamente."""
        validator = CrossValidator(SimpleModel, device="cpu")
        
        assert validator.model_class == SimpleModel
        assert validator.device == "cpu"
    
    def test_compute_metrics(self):
        """Verifica cálculo de métricas."""
        validator = CrossValidator(SimpleModel, device="cpu")
        
        fold_losses = [0.5, 0.4, 0.45]
        fold_accuracies = [0.8, 0.85, 0.82]
        
        metrics = validator._compute_metrics(fold_losses, fold_accuracies)
        
        assert metrics.mean_loss == pytest.approx(np.mean(fold_losses))
        assert metrics.mean_accuracy == pytest.approx(np.mean(fold_accuracies))
        assert metrics.std_loss == pytest.approx(np.std(fold_losses))
        assert metrics.std_accuracy == pytest.approx(np.std(fold_accuracies))
        assert isinstance(metrics.variance_coefficient, float)


# ============================================================================
# Tests for ModelEvaluator
# ============================================================================

class TestModelEvaluator:
    """Testes para avaliação de modelos."""
    
    def test_init(self):
        """Verifica se inicializa corretamente."""
        model = SimpleModel()
        evaluator = ModelEvaluator(model, device="cpu")
        
        assert evaluator.model == model
        assert evaluator.device == "cpu"
        assert len(evaluator.predictions) == 0
    
    def test_analyze_errors(self):
        """Verifica análise de erros."""
        model = SimpleModel()
        evaluator = ModelEvaluator(model, device="cpu")
        
        # Simular predições
        evaluator.predictions = [0, 0, 1, 1, 0, 1]
        evaluator.targets = [0, 1, 1, 0, 0, 1]
        
        error_analysis = evaluator.analyze_errors()
        
        assert "total_errors" in error_analysis
        assert "error_rate" in error_analysis
        assert "errors_by_class" in error_analysis
        assert error_analysis["total_errors"] == 2
    
    def test_generate_report(self):
        """Verifica geração de relatório."""
        model = SimpleModel()
        evaluator = ModelEvaluator(model, device="cpu")
        
        # Simular resultados
        evaluator.predictions = [0, 0, 1, 1] * 25
        evaluator.targets = [0, 1, 1, 0] * 25
        evaluator.losses = [0.5] * 100
        evaluator.class_names = ["class_0", "class_1"]
        evaluator._compute_metrics()
        
        report = evaluator.generate_report()
        
        assert "MODEL EVALUATION REPORT" in report
        assert "OVERALL METRICS" in report
        assert "PER-CLASS METRICS" in report


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase33Integration:
    """Testes de integração para Phase 3.3."""
    
    def test_finetune_workflow(self):
        """Testa fluxo completo de fine-tuning."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            model = SimpleModel()
            trainer = MagicMock()
            trainer.save_checkpoint = MagicMock()
            
            learner = FinetuneLearner(model, trainer, device="cpu")
            
            # Configure
            config = FinetuneConfig(
                learning_rate=0.001,
                epochs=2,
                freeze_backbone=True,
            )
            
            # Setup optimizer
            learner.setup_optimizer(config)
            
            assert learner.optimizer is not None
            assert learner.scheduler is not None
    
    def test_evaluation_workflow(self):
        """Testa fluxo completo de avaliação."""
        model = SimpleModel()
        evaluator = ModelEvaluator(model, device="cpu")
        
        # Simular dados
        X = torch.randn(100, 10)
        y = torch.randint(0, 2, (100,))
        
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=32)
        
        # Simular resultados
        evaluator.predictions = [0, 1] * 50
        evaluator.targets = [0, 1] * 50
        evaluator.losses = [0.5] * 50
        evaluator.class_names = ["class_0", "class_1"]
        evaluator._compute_metrics()
        
        # Verificar
        assert evaluator.metrics is not None
        assert evaluator.metrics.accuracy == pytest.approx(1.0)


# ============================================================================
# Performance Tests
# ============================================================================

class TestPhase33Performance:
    """Testes de performance para Phase 3.3."""
    
    def test_finetuner_memory_efficiency(self):
        """Verifica eficiência de memória do fine-tuner."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        
        # Congelar backbone economiza memória
        learner._freeze_backbone()
        
        # Verificar que menos parâmetros requerem gradientes
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())
        
        # Deve ter menos parâmetros treináveis que o total
        assert trainable_params < total_params


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestPhase33EdgeCases:
    """Testes de casos extremos."""
    
    def test_finetuner_empty_dataset(self):
        """Testa fine-tuner com dataset vazio."""
        model = SimpleModel()
        trainer = MagicMock()
        
        learner = FinetuneLearner(model, trainer, device="cpu")
        learner.results["train_losses"] = []
        learner.results["val_accuracies"] = []
        
        learner._generate_summary()
        
        assert learner.results["summary"]["total_epochs_trained"] == 0
    
    def test_evaluator_perfect_predictions(self):
        """Testa avaliador com predições perfeitas."""
        model = SimpleModel()
        evaluator = ModelEvaluator(model, device="cpu")
        
        # Predições perfeitas
        evaluator.predictions = [0, 1, 0, 1] * 25
        evaluator.targets = [0, 1, 0, 1] * 25
        evaluator.losses = [0.0] * 100
        evaluator.class_names = ["class_0", "class_1"]
        evaluator._compute_metrics()
        
        assert evaluator.metrics.accuracy == 1.0
        
        error_analysis = evaluator.analyze_errors()
        assert error_analysis["total_errors"] == 0
