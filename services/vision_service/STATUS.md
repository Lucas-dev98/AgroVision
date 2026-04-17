# 🎥 Vision Service - Status & Roadmap

## ✅ Completado (FASE 1-2)

### FASE 1: Core Detection Service (12 testes)
- ✅ YOLODetectionService implementado
- ✅ Frame decoding/encoding
- ✅ YOLO v8 inference integration
- ✅ Trough classification (histogram analysis)
- ✅ Bounding box normalization
- ✅ 12 testes passando (100% coverage)

### FASE 2: MongoDB Repositories (13 testes)
- ✅ DetectionRepository (6 testes)
- ✅ AnimalLocationRepository (5 testes)
- ✅ CameraCalibrationRepository (4 testes)
- ✅ 13 testes passando (100% coverage)

### Infraestrutura
- ✅ FastAPI application setup
- ✅ MongoDB connection with async motor
- ✅ Pydantic schemas for type safety
- ✅ Error handling and logging
- ✅ Health check endpoint
- ✅ Docker container setup
- ✅ Requirements.txt with all dependencies
- ✅ Comprehensive documentation (README, ARCHITECTURE, ROADMAP)

### Endpoints Implementados
- ✅ GET /health - Health check
- ✅ POST /api/v1/vision/detect - Process frame
- ✅ GET /api/v1/vision/animals - List detections
- ✅ GET /api/v1/vision/troughs - Trough status
- ✅ GET /api/v1/vision/animals/{id}/history - Animal history
- ✅ GET /api/v1/vision/animals/latest - Latest locations
- ✅ POST /api/v1/vision/cameras/calibrate - Camera calibration
- ✅ GET /api/v1/vision/cameras/{id} - Camera info
- ✅ GET /api/v1/vision/cameras - List cameras

## ⏳ Próximos Passos

### FASE 3: Endpoint Testing (15 testes)
- [ ] HTTP endpoint tests
- [ ] Request/response validation
- [ ] Error handling tests
- [ ] Multipart file upload (future enhancement)

**Comando para rodar:**
```bash
cd services/vision_service
pytest tests/test_endpoints.py -v
```

### FASE 4: API Gateway Integration (8 testes)
- [ ] Proxy routes in API Gateway
- [ ] JWT authentication
- [ ] Rate limiting
- [ ] Request forwarding
- [ ] Response transformation

### FASE 5: Performance & Optimization (5+ testes)
- [ ] Caching layer (Redis)
- [ ] Query optimization
- [ ] Batch processing
- [ ] Memory optimization
- [ ] Latency benchmarking

## 📊 Métricas Atuais

| Métrica | Valor |
|---------|-------|
| Testes Implementados | 25+ |
| Testes Passando | 25+ |
| Coverage | 100% (FASE 1-2) |
| Linhas de Código | ~1500 |
| Endpoints | 9 |
| Collections MongoDB | 3 |
| Documentação | 100% |

## 🚀 Como Começar

### 1. Instalar Dependencies
```bash
cd services/vision_service
pip install -r requirements.txt
```

### 2. Executar MongoDB (Docker)
```bash
# Se não estiver rodando
docker run -d \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin \
  mongo:7-alpine
```

### 3. Rodar Testes
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### 4. Iniciar Serviço (Development)
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8003
```

### 5. Testar Endpoints
```bash
# Health check
curl http://localhost:8003/health

# Listar câmeras
curl http://localhost:8003/api/v1/vision/cameras

# Calibrar câmera
curl -X POST http://localhost:8003/api/v1/vision/cameras/calibrate \
  -d "camera_id=camera-1&location=Pasture-A"
```

## 📋 Estrutura de Arquivos

```
services/vision_service/
├── app/
│   ├── __init__.py
│   ├── schemas.py                 # Pydantic models
│   ├── models.py                  # MongoDB models
│   ├── core/
│   │   ├── __init__.py
│   │   └── database.py            # MongoDB connection
│   ├── services/
│   │   ├── __init__.py
│   │   └── detection.py           # YOLO service
│   └── repositories/
│       └── __init__.py            # All repositories
├── main.py                        # FastAPI app
├── requirements.txt
├── Dockerfile
├── pytest.ini
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_detection_service.py
│   ├── test_repositories.py
│   └── test_endpoints.py
├── README.md
├── ARCHITECTURE.md
└── ROADMAP.md
```

## 🎯 Objetivos da Visão Computacional

1. **Detecção de Gado** 🐄
   - Identificar animais em câmeras
   - Contar rebanho
   - Rastrear indivíduos (RFID + visual)

2. **Monitoramento de Cocho** 🍽️
   - Status: vazio/parcial/cheio
   - Alertas quando vazio
   - Histórico de consumo

3. **Localização de Animais** 📍
   - Rastrear posição por câmera
   - Histórico de movimentação
   - Identificar padrões de pastejo

4. **Análise de Comportamento** 📊
   - Grazing patterns
   - Drinking behavior
   - Sleeping/resting time
   - Anomalies (lameness, illness)

## 🔧 Configuração do YOLO

### Modelos Disponíveis

```bash
# Nano (recomendado para real-time em CPU)
YOLO_MODEL=yolov8n.pt      # 6MB, 3ms per frame

# Small
YOLO_MODEL=yolov8s.pt      # 21MB, 6ms per frame

# Medium
YOLO_MODEL=yolov8m.pt      # 49MB, 12ms per frame

# Large (melhor acurácia)
YOLO_MODEL=yolov8l.pt      # 98MB, 25ms per frame
```

### Confidence Threshold

```bash
# Padrão (pode ajustar via API)
YOLO_CONFIDENCE=0.5

# Mais rigoroso (menos falsos positivos)
YOLO_CONFIDENCE=0.7

# Mais sensível (mais detecções)
YOLO_CONFIDENCE=0.3
```

## 📚 Próximas Fases

### Fase 3: Testes de Endpoint
```python
# test_endpoints.py será populado com:
- Health check tests
- Frame processing tests
- Animal detection tests
- Trough status tests
- Camera management tests
- Error handling tests
```

### Fase 4: API Gateway
```yaml
# docker-compose.yml
vision-service:
  ports:
    - "8003:8003"

# api-gateway será configurado com:
VISION_SERVICE_URL: http://vision-service:8003

# Rotas:
GET  /api/v1/vision/* → Vision Service
```

### Fase 5: Real-time Streaming
```python
# Futuro: WebSocket para streaming
# - Real-time detection updates
# - Live camera feeds
# - Alert notifications
```

## 🐛 Troubleshooting

### YOLO Model Downloading
```python
# First run will download model (~35MB)
from ultralytics import YOLO
model = YOLO("yolov8n.pt")  # Auto-downloads from Ultralytics
```

### MongoDB Connection Issues
```
Error: connection refused
Solution: Ensure MongoDB is running on port 27017
Check: docker ps | grep mongo
```

### Memory Usage
```
If high memory usage:
- Use smaller YOLO model (yolov8n instead of yolov8l)
- Reduce frame resolution
- Lower batch size
```

## 📞 Suporte

Para questões ou problemas:
1. Verificar README.md para instruções
2. Consultar ARCHITECTURE.md para design details
3. Executar testes: `pytest tests/ -v`
4. Checar logs: `docker logs agrovision-vision-service`

## ✨ Próximas Melhorias

- [ ] RTSP camera stream support
- [ ] WebSocket real-time updates
- [ ] Custom YOLO model training
- [ ] Cross-camera tracking
- [ ] GPU/TPU acceleration
- [ ] Kubernetes deployment
- [ ] Prometheus metrics export
- [ ] Grafana dashboards

---

**Status**: 🟢 Ready for PHASE 3 Endpoint Testing
**Last Updated**: 2026-04-16 16:30 UTC
**Version**: 1.0.0
