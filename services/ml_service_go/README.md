# ML Service (Machine Learning)

Serviço Go para gerenciamento de modelos de machine learning, treinamento e predição.

## 📋 Requisitos

- Go 1.21+
- Gin web framework

## 🚀 Instalação Rápida

```bash
cd /home/lucasbastos/AgroVision/services/ml_service_go

# Copiar .env
cp .env.example .env

# Download dependencies
go mod download

# Build
go build -o ml-service ./cmd/main

# Run
./ml-service
```

## 🐳 Docker

```bash
docker build -t agrovision/ml-service .
docker run -p 8004:8004 agrovision/ml-service
```

## 📡 API Endpoints

### GET /ml/models
Listar todos os modelos disponíveis.

```bash
curl http://localhost:8004/ml/models
```

**Response:**
```json
{
  "models": [
    {
      "id": "model_1",
      "name": "Detecção de Anomalias",
      "type": "anomaly_detection",
      "status": "active",
      "accuracy": 0.94,
      "last_trained": "2026-04-28T10:00:00Z",
      "version": "2.1.0"
    }
  ],
  "total": 3
}
```

### GET /ml/models/:id
Recuperar detalhes de um modelo específico.

```bash
curl http://localhost:8004/ml/models/model_1
```

### POST /ml/train
Iniciar treinamento de um modelo.

**Request:**
```bash
curl -X POST http://localhost:8004/ml/train \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "model_1",
    "epochs": 10,
    "batch_size": 32,
    "learning_rate": 0.001
  }'
```

**Response:**
```json
{
  "message": "Training started",
  "model_id": "model_1",
  "old_status": "active",
  "new_status": "training",
  "epochs": 10,
  "batch_size": 32,
  "learning_rate": 0.001
}
```

### POST /ml/predict
Fazer predição usando um modelo.

**Request:**
```bash
curl -X POST http://localhost:8004/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "model_1",
    "input": "dados de entrada"
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "model_id": "model_1",
  "input": "dados de entrada",
  "output": "Resultado simulado...",
  "confidence": 0.87,
  "created_at": "2026-05-05T14:30:00Z"
}
```

### GET /ml/predictions
Listar todas as predições realizadas.

```bash
curl http://localhost:8004/ml/predictions
```

### GET /ml/predictions/:id
Recuperar detalhes de uma predição específica.

```bash
curl http://localhost:8004/ml/predictions/{predictionId}
```

### GET /health
Health check.

```bash
curl http://localhost:8004/health
```

## 🔧 Configuração

`.env`:
```
ML_SERVICE_PORT=8004
ML_SERVICE_HOSTNAME=0.0.0.0
```

## 📝 Notas

- Porta padrão: **8004**
- Começa com 3 modelos mock pré-configurados
- Treinamento simulado com delay de 5 segundos
- Predições retornam resultado simulado
- Em produção, integrar frameworks reais (TensorFlow, PyTorch, etc)

## 🔌 Integração com API Gateway

O API Gateway em `localhost:9000` já está configurado para rotear:
- `GET /api/v1/ml/models` → ML Service `/ml/models`
- `GET /api/v1/ml/models/:id` → ML Service `/ml/models/:id`
- `POST /api/v1/ml/train` → ML Service `/ml/train`
- `POST /api/v1/ml/predict` → ML Service `/ml/predict`
- `GET /api/v1/ml/predictions` → ML Service `/ml/predictions`
- `GET /api/v1/ml/predictions/:id` → ML Service `/ml/predictions/:id`

## 🎓 Modelos Disponíveis

1. **Detecção de Anomalias** (model_1)
   - Tipo: anomaly_detection
   - Status: active
   - Acurácia: 94%

2. **Classificação de Comportamento** (model_2)
   - Tipo: behavior_classification
   - Status: active
   - Acurácia: 88%

3. **Predição de Peso** (model_3)
   - Tipo: prediction
   - Status: training
   - Versão: 3.0.0-beta
