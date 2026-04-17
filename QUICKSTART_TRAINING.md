# 🚀 Como Treinar os Modelos - Quick Start

## 3 Formas Rápidas para Treinar

### ✅ Opção 1: Script Automático (RECOMENDADO - Mais Fácil)

```bash
# Modo interativo (escolher opção)
./train_models.sh

# Ou direto com argumentos
./train_models.sh --quick              # Dados sintéticos (~30 min)
./train_models.sh --real               # Dados reais MongoDB (~2-3 horas)
./train_models.sh --finetune           # Transfer learning (~30 min)
./train_models.sh --all                # Pipeline completo (~3-4 horas)
```

### ✅ Opção 2: Linha de Comando Direta

```bash
cd services/ml_service

# Treinar um modelo
python -m app.training.train_real_data --model behavior --epochs 50 --device cpu

# Treinar todos
for model in behavior anomaly reid temporal; do
    python -m app.training.train_real_data --model $model --epochs 50 --device cpu
done
```

### ✅ Opção 3: Python Script (Para Integração)

```python
import asyncio
import torch
from app.training.train_real_data import train_with_real_data
import argparse

async def main():
    args = argparse.Namespace(
        model="behavior",
        epochs=50,
        batch_size=32,
        device="cuda" if torch.cuda.is_available() else "cpu",
        learning_rate=0.001,
        use_real_data=False,
        resume_checkpoint=False,
        list_models=False,
    )
    await train_with_real_data(args)

asyncio.run(main())
```

---

## 📊 Comparação de Opções

| Opção | Tempo | GPU | Dados | Recomendado Para |
|-------|-------|-----|-------|------------------|
| Dados Sintéticos | 15-30 min | ❌ | Sintéticos | Quick start, testes |
| Dados Reais | 1-3 horas | ✅ | MongoDB | Produção |
| Fine-tuning | 30-60 min | ✅ | Reais | Produção (+10% acc) |
| Pipeline Completo | 3-4 horas | ✅ | Ambos | Deployment final |

---

## 🎯 Recomendação

Para começar **AGORA**, execute:

```bash
# 1. Ativar ambiente (se ainda não estiver)
source venv/bin/activate

# 2. Executar o script
./train_models.sh

# 3. Escolher opção 1 (Quick - dados sintéticos)
# Vai treinar todos os 4 modelos em ~30 minutos
```

**Resultado esperado:**
- ✅ 4 modelos treinados
- ✅ Checkpoints salvos em `models/`
- ✅ Prontos para usar na PredictionService

---

## 📝 Após Treinamento

```bash
# 1. Testar modelos treinados
pytest tests/test_phase34_prediction_api.py -v

# 2. Ver checkpoints
ls -lh services/ml_service/models/

# 3. Prosseguir para Task 2 (Model Optimization)
# - ONNX export
# - Quantization
# - TensorRT optimization
```

---

## 🆘 Ajuda

```bash
# Ver todas as opções
./train_models.sh --help

# Ver documentação completa
cat GUIDE_MODEL_TRAINING.md

# Treinar modelo específico
./train_models.sh behavior

# Treinar com GPU
./train_models.sh --device cuda
```

---

**Vamos treinar? Execute: `./train_models.sh`** 🚀
