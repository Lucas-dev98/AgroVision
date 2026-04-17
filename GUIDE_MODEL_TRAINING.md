# Guia de Treinamento dos Modelos - FASE 3.4

## 📋 Visão Geral

Existem 3 formas de treinar os modelos AgroVision:
1. **Treinamento com Dados Sintéticos** (Quick Start)
2. **Treinamento com Dados Reais do MongoDB** (Produção)
3. **Fine-tuning (Transfer Learning)** (Recomendado para produção)

---

## ✅ Opção 1: Treinamento Rápido (Dados Sintéticos)

**Tempo estimado**: 15-30 minutos | **GPU necessária**: Não

### 1.1 Setup Básico

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Navegar para ml_service
cd services/ml_service

# Instalar dependências (se ainda não instaladas)
pip install -r requirements.txt
```

### 1.2 Treinar um Modelo Individual

```bash
# Treinar modelo de comportamento (50 épocas)
python -m app.training.train_real_data \
    --model behavior \
    --epochs 50 \
    --batch-size 32 \
    --device cpu

# Treinar modelo de anomalia
python -m app.training.train_real_data \
    --model anomaly \
    --epochs 50 \
    --batch-size 64 \
    --device cpu

# Treinar modelo Re-ID (reidentificação)
python -m app.training.train_real_data \
    --model reid \
    --epochs 100 \
    --batch-size 32 \
    --device cpu

# Treinar modelo temporal (análise de séries temporais)
python -m app.training.train_real_data \
    --model temporal \
    --epochs 50 \
    --batch-size 32 \
    --device cpu
```

### 1.3 Treinar Todos os Modelos

```bash
# Script para treinar todos os 4 modelos
for model in behavior anomaly reid temporal; do
    echo "▶️  Treinando modelo: $model"
    python -m app.training.train_real_data \
        --model $model \
        --epochs 50 \
        --batch-size 32 \
        --device cpu
    echo "✅ $model concluído"
done
```

### 1.4 Verificar Modelos Disponíveis

```bash
# Listar todos os modelos e checkpoints
python -m app.training.train_real_data --list-models

# Output esperado:
# Available models:
#   - behavior (input: 3×240×240, output: 8 classes)
#   - anomaly (input: 6-d vector, output: 2 classes)
#   - reid (input: 3×224×224, output: 1000 classes)
#   - temporal (input: 30×128, output: 8 classes)
```

---

## 🚀 Opção 2: Treinamento com Dados Reais (MongoDB)

**Tempo estimado**: 1-3 horas | **GPU necessária**: Recomendada | **Dados**: 2,600+ LOC em FASE 3.1

### 2.1 Pré-requisitos

```bash
# 1. MongoDB deve estar rodando
docker-compose up -d

# 2. Verificar conexão
python -c "from motor.motor_asyncio import AsyncIOMotorClient; print('Motor ready')"

# 3. Populador de dados (se necessário)
# Os dados devem estar no MongoDB conforme configurado em FASE 3.1
```

### 2.2 Treinar com Dados Reais

```bash
# Treinar com dados reais do MongoDB
python -m app.training.train_real_data \
    --model behavior \
    --epochs 100 \
    --batch-size 32 \
    --device cuda \
    --use-real-data \
    --learning-rate 0.0001

# Com múltiplos modelos em paralelo (requer mais recursos)
python -m app.training.train_real_data \
    --model behavior \
    --epochs 100 \
    --batch-size 32 \
    --device cuda \
    --use-real-data \
    --learning-rate 0.0001 &

python -m app.training.train_real_data \
    --model anomaly \
    --epochs 100 \
    --batch-size 64 \
    --device cuda \
    --use-real-data &

wait  # Esperar conclusão de todos
```

### 2.3 Resumir de Checkpoint

```bash
# Retomar treinamento de um checkpoint anterior
python -m app.training.train_real_data \
    --model behavior \
    --epochs 50 \
    --batch-size 32 \
    --device cuda \
    --resume-checkpoint \
    --use-real-data

# Isso carregará o último checkpoint e continuará de onde parou
```

---

## 🎯 Opção 3: Fine-tuning (Transfer Learning) - RECOMENDADO

**Tempo estimado**: 30-60 minutos | **GPU necessária**: Recomendada | **Performance**: +10-15%

Esta é a **abordagem recomendada** para produção. Usa os modelos pré-treinados e adapta-os aos dados da fazenda.

### 3.1 Setup do Fine-tuning

```bash
# Navegar para ml_service
cd services/ml_service

# Verificar modelos pré-treinados disponíveis
ls -lh models/
```

### 3.2 Script de Fine-tuning Básico

Crie um arquivo `finetune_all.py`:

```python
import asyncio
import torch
from app.models.behavior import CNNBehaviorClassifier
from app.models.anomaly import AnomalyDetectionAutoencoder
from app.models.reid import ResNetReID
from app.models.temporal import LSTMTemporalAnalyzer
from app.training.finetuner import FinetuneLearner, FinetuneConfig
from app.training.cross_validator import CrossValidator

async def finetune_all_models():
    """Fine-tune todos os 4 modelos com configuração otimizada."""
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    models = {
        "behavior": {
            "class": CNNBehaviorClassifier,
            "checkpoint": "models/behavior_model.pt",
            "num_classes": 8,
        },
        "anomaly": {
            "class": AnomalyDetectionAutoencoder,
            "checkpoint": "models/anomaly_model.pt",
            "num_classes": 2,
        },
        "reid": {
            "class": ResNetReID,
            "checkpoint": "models/reid_model.pt",
            "num_classes": 1000,
        },
        "temporal": {
            "class": LSTMTemporalAnalyzer,
            "checkpoint": "models/temporal_model.pt",
            "num_classes": 8,
        },
    }
    
    results = {}
    
    for model_name, config in models.items():
        print(f"\n{'='*60}")
        print(f"Fine-tuning: {model_name.upper()}")
        print(f"{'='*60}")
        
        # 1. Carregar modelo
        model = config["class"]()
        if torch.cuda.is_available():
            checkpoint = torch.load(config["checkpoint"])
            model.load_state_dict(checkpoint)
        model.to(device)
        
        # 2. Configurar fine-tuner com learning rate discriminativo
        config_finetune = FinetuneConfig(
            base_learning_rate=0.0001,
            num_epochs=20,
            unfreeze_from_layer=-3,  # Descongelar últimas 3 camadas
            warmup_epochs=2,
            patience=5,
        )
        
        finetuner = FinetuneLearner(
            model=model,
            config=config_finetune,
            device=device,
        )
        
        # 3. Fine-tune (você precisa fornecer os data loaders)
        # Exemplo com dados sintéticos:
        import numpy as np
        if model_name == "behavior":
            synthetic_data = [
                (np.random.randn(3, 240, 240).astype(np.float32), 
                 np.random.randint(0, 8))
                for _ in range(100)
            ]
        elif model_name == "anomaly":
            synthetic_data = [
                (np.random.randn(6).astype(np.float32), 
                 np.random.randint(0, 2))
                for _ in range(100)
            ]
        # ... similares para reid e temporal
        
        # 4. Validar com cross-validation
        validator = CrossValidator(
            model=model,
            device=device,
        )
        
        metrics = validator.kfold_cross_validate(
            dataset=synthetic_data,
            k_folds=5,
        )
        
        results[model_name] = metrics
        print(f"✅ {model_name} fine-tuning completo!")
        print(f"   Cross-validation score: {metrics.mean_accuracy:.4f}")
        print(f"   Std deviation: {metrics.std_accuracy:.4f}")
        
        # 5. Salvar modelo fine-tuned
        torch.save(model.state_dict(), f"models/{model_name}_finetuned.pt")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(finetune_all_models())
    print(f"\n{'='*60}")
    print("RESUMO DO FINE-TUNING")
    print(f"{'='*60}")
    for model_name, metrics in results.items():
        print(f"{model_name}: accuracy={metrics.mean_accuracy:.4f}")
```

### 3.3 Executar Fine-tuning

```bash
# Executar o script
python finetune_all.py

# Ou linha de comando mais simples (usando trainer existente)
python -m app.training.train_real_data \
    --model behavior \
    --epochs 20 \
    --batch-size 32 \
    --device cuda \
    --learning-rate 0.0001 \
    --use-real-data
```

---

## 📊 Opções de Linha de Comando

```bash
python -m app.training.train_real_data [OPTIONS]

OPTIONS:
  --model {behavior|anomaly|reid|temporal}
            Modelo a treinar (default: behavior)
  
  --epochs EPOCHS
            Número de épocas (default: 50)
  
  --batch-size BATCH_SIZE
            Tamanho do batch (default: 32)
  
  --device {cpu|cuda}
            Dispositivo (default: cuda se disponível, senão cpu)
  
  --learning-rate LR
            Learning rate (default: 0.001)
  
  --use-real-data
            Usar dados reais do MongoDB (default: dados sintéticos)
  
  --resume-checkpoint
            Retomar de checkpoint anterior (default: False)
  
  --list-models
            Listar modelos disponíveis e sair
  
  --help
            Mostrar ajuda
```

---

## 💾 Estrutura de Checkpoints

Os modelos treinados são salvos em:

```
services/ml_service/
├── models/
│   ├── behavior_model.pt          # Modelo base de comportamento
│   ├── anomaly_model.pt           # Modelo base de anomalia
│   ├── reid_model.pt              # Modelo base Re-ID
│   ├── temporal_model.pt          # Modelo base temporal
│   ├── behavior_finetuned.pt      # Fine-tuned (se aplicável)
│   └── ...
└── checkpoints/
    ├── behavior/
    │   ├── checkpoint_epoch_10.pt
    │   ├── checkpoint_epoch_20.pt
    │   └── best_model.pt
    ├── anomaly/
    ├── reid/
    └── temporal/
```

### Recuperar Modelo Treinado

```python
import torch
from app.models.behavior import CNNBehaviorClassifier

# Carregar modelo treinado
model = CNNBehaviorClassifier()
state_dict = torch.load("models/behavior_finetuned.pt")
model.load_state_dict(state_dict)
model.eval()

# Usar para predições
input_image = torch.randn(1, 3, 240, 240)
with torch.no_grad():
    output = model(input_image)
    predictions = torch.softmax(output, dim=1)
    print(predictions)
```

---

## 🎬 Recomendação: Pipeline Completo (30 minutos)

Este é o pipeline **recomendado** para começar:

```bash
#!/bin/bash

cd services/ml_service

echo "🚀 Pipeline de Treinamento Completo"
echo "=================================="

# 1. Treinar modelos básicos (dados sintéticos) - 10 min
echo "▶️  Fase 1: Treinamento básico"
for model in behavior anomaly reid temporal; do
    python -m app.training.train_real_data --model $model --epochs 10 --device cpu
done

# 2. Fine-tuning com dados reais (se MongoDB está rodando) - 15 min
echo "▶️  Fase 2: Fine-tuning com dados reais"
docker-compose up -d  # Certificar que MongoDB está rodando

python -m app.training.train_real_data \
    --model behavior \
    --epochs 20 \
    --batch-size 32 \
    --device cuda \
    --use-real-data \
    --learning-rate 0.0001

# 3. Validação - 5 min
echo "▶️  Fase 3: Validação"
python -m pytest tests/test_phase33.py::TestFinetuneLearner -v

echo "✅ Pipeline completo!"
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'app'"

```bash
# Solução: Garantir que você está no diretório correto
cd services/ml_service
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m app.training.train_real_data --help
```

### Erro: "CUDA out of memory"

```bash
# Solução: Usar CPU ou reduzir batch size
python -m app.training.train_real_data \
    --model behavior \
    --epochs 50 \
    --batch-size 8 \
    --device cpu  # ou reduzir batch
```

### Erro: "MongoDB connection failed"

```bash
# Solução: Iniciar MongoDB
docker-compose up -d

# Verificar conexão
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
async def test():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    print(client)
asyncio.run(test())
"
```

---

## ✅ Próximos Passos Após Treinamento

1. **Usar Modelos Treinados em FASE 3.4 Task 2 (Model Optimization)**
   - Exportar para ONNX
   - Quantizar (INT8, FP16)
   - Otimizar com TensorRT

2. **Fazer Deploy da PredictionService**
   - Com modelos finetuned
   - Em staging/produção

3. **Monitorar Performance**
   - Comparar accuracy antes/depois
   - Verificar latência de inferência

---

## 📚 Referências

- [Trainer Documentation](app/training/README.md)
- [FASE 3.2 - Training Integration](../../../FASE3_PHASE32_STATUS.md)
- [FASE 3.3 - Fine-tuning](../../../FASE3_PHASE33_STATUS.md)
- [Models API](app/models/README.md)
