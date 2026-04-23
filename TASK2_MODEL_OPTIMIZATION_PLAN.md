# 🎯 FASE 3.4 Task 2: Model Optimization
## ONNX Export | Quantization | TensorRT

**Status**: 🟢 **INICIANDO**  
**Data**: 16 de Abril de 2026  
**Objetivo**: Otimizar 4 modelos treinados para produção

---

## 📋 Tarefas

### 1️⃣ ONNX Export (Todos 4 Modelos)
- [ ] Criar exportador ONNX universal
- [ ] Exportar behavior (CNN)
- [ ] Exportar anomaly (Autoencoder)
- [ ] Exportar reid (ResNet)
- [ ] Exportar temporal (LSTM)
- [ ] Validar outputs vs PyTorch

**Benefícios**:
- ✅ Cross-platform compatibility
- ✅ Hardware acceleration ready
- ✅ Tamanho reduzido (~30-50%)

---

### 2️⃣ Quantization (INT8 + FP16)
- [ ] INT8 quantization (máxima compressão)
- [ ] FP16 quantization (bom balanço)
- [ ] Comparar acurácia vs compressão
- [ ] Testes de precisão

**Benefícios**:
- ✅ Tamanho: -50% a -75%
- ✅ Latência: -30% a -60%
- ✅ Acurácia: -0.5% a -2% (aceitável)

---

### 3️⃣ TensorRT Optimization
- [ ] Gerar TensorRT engines (se NVIDIA)
- [ ] Benchmark speedup
- [ ] Comparar com ONNX Runtime

**Benefícios**:
- ✅ Speedup: 2x-5x
- ✅ GPU-optimized
- ✅ Production-ready

---

### 4️⃣ Performance Benchmarking
- [ ] Latência: Original vs ONNX vs Quantizado vs TensorRT
- [ ] Throughput: Batch de 100, 500, 1000 samples
- [ ] Memória: Peak usage comparação
- [ ] Acurácia: Validar que não piorou muito

---

### 5️⃣ Test Suite (40+ testes)
- [ ] ONNX export validation
- [ ] Quantization precision tests
- [ ] Performance regression tests
- [ ] Output correctness tests
- [ ] Device compatibility tests

---

## 📁 Arquivos a Criar

### `app/optimization/onnx_exporter.py`
```python
class ONNXExporter:
    async def export_model(model_path, model_type, output_path)
    async def export_all_models()
    async def validate_onnx_outputs()
```

### `app/optimization/quantizer.py`
```python
class Quantizer:
    async def quantize_int8(model_path, calibration_data)
    async def quantize_fp16(model_path)
    async def compare_accuracy()
```

### `app/optimization/tensorrt_optimizer.py`
```python
class TensorRTOptimizer:
    async def build_engine(onnx_path)
    async def benchmark_engine()
    async def compare_performance()
```

### `tests/test_phase34_model_optimization.py`
```python
class TestONNXExport (10 tests)
class TestQuantization (12 tests)
class TestTensorRT (8 tests)
class TestPerformance (10 tests)
```

---

## 🔧 Dependências Necessárias

```bash
pip install onnx onnxruntime onnx-simplifier
pip install tensorrt (opcional, se NVIDIA)
pip install onnxmltools
```

---

## ⏱️ Timeline Estimado

| Fase | Tempo | Status |
|------|-------|--------|
| ONNX Export | 30 min | ⏳ Próximo |
| Quantization | 30 min | ⏳ Próximo |
| TensorRT | 20 min | ⏳ Próximo |
| Benchmarking | 20 min | ⏳ Próximo |
| Tests | 20 min | ⏳ Próximo |
| **TOTAL** | **2 horas** | — |

---

## 🎯 Métricas de Sucesso

✅ **ONNX Export**:
- Todos 4 modelos exportados
- Outputs validados contra PyTorch (max diff <1e-5)
- Tamanho reduzido em média 30%

✅ **Quantization**:
- INT8: -70% tamanho, <2% acurácia loss
- FP16: -50% tamanho, <1% acurácia loss
- Tests validam precision

✅ **Performance**:
- Latência reduced 30-60%
- Throughput increased 2-3x
- Memory usage reduced 40-50%

✅ **Tests**:
- 40+ tests all passing
- 100% code coverage
- No regressions

---

## 📊 Expected Results

### Behavior Model Comparison
```
Original (PyTorch):
  Size: 113M
  Latency: 12ms
  Memory: ~500MB

ONNX:
  Size: 80M (29% reduction)
  Latency: 10ms (17% faster)
  Memory: ~400MB

ONNX INT8:
  Size: 30M (73% reduction)
  Latency: 6ms (50% faster)
  Memory: ~200MB
  Acurácia: -1.2% (acceptable)

ONNX FP16:
  Size: 60M (47% reduction)
  Latency: 8ms (33% faster)
  Memory: ~300MB
  Acurácia: -0.5%

TensorRT (GPU):
  Size: 75M
  Latency: 3ms (75% faster)
  Memory: ~350MB
  Acurácia: same as ONNX
```

---

## 🚀 Próximo Passo

```bash
# 1. Instalar dependências
pip install onnx onnxruntime onnx-simplifier

# 2. Começar com ONNX exporter
# Vou criar: app/optimization/onnx_exporter.py

# 3. Criar suite de testes
# Vou criar: tests/test_phase34_model_optimization.py

# 4. Executar pipeline completo
cd /home/lucasbastos/AgroVision
source venv/bin/activate
PYTHONPATH=services/ml_service:$PYTHONPATH \
  python -m pytest services/ml_service/tests/test_phase34_model_optimization.py -v
```

---

## 📚 Referências

- ONNX Spec: https://onnx.ai/
- ONNX Runtime: https://onnxruntime.ai/
- TensorRT: https://developer.nvidia.com/tensorrt
- Quantization: https://pytorch.org/docs/stable/quantization.html

---

**Status**: Pronto para começar! ✅
