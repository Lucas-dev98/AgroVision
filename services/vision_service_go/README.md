# Vision Service (YOLO Detection)

Serviço Go para detecção de animais usando YOLO em imagens.

## 📋 Requisitos

- Go 1.21+
- Gin web framework

## 🚀 Instalação Rápida

```bash
cd /home/lucasbastos/AgroVision/services/vision_service_go

# Copiar .env
cp .env.example .env

# Download dependencies
go mod download

# Build
go build -o vision-service ./cmd/main

# Run
./vision-service
```

## 🐳 Docker

```bash
docker build -t agrovision/vision-service .
docker run -p 8003:8003 agrovision/vision-service
```

## 📡 API Endpoints

### POST /vision/detect
Upload de imagem para detecção YOLO.

**Request:**
```bash
curl -X POST -F "image=@photo.jpg" http://localhost:8003/vision/detect
```

**Response:**
```json
{
  "id": "uuid",
  "image_url": "file://photo.jpg",
  "detections": [
    {
      "class": "animal",
      "confidence": 0.95,
      "bbox": [100, 150, 300, 450]
    }
  ],
  "created_at": "2026-05-05T14:30:00Z"
}
```

### GET /vision/results/:id
Recuperar resultado de detecção.

```bash
curl http://localhost:8003/vision/results/{resultId}
```

### GET /vision/results
Listar todos os resultados.

```bash
curl http://localhost:8003/vision/results
```

### GET /health
Health check.

```bash
curl http://localhost:8003/health
```

## 🔧 Configuração

`.env`:
```
VISION_SERVICE_PORT=8003
VISION_SERVICE_HOSTNAME=0.0.0.0
```

## 📝 Notas

- Porta padrão: **8003**
- Atualmente faz simulação de YOLO com dados mock
- Em produção, integrar modelo YOLO real (YOLOv8, etc)
- Suporta upload de múltiplas imagens

## 🔌 Integração com API Gateway

O API Gateway em `localhost:9000` já está configurado para rotear:
- `POST /api/v1/vision/detect` → Vision Service `/vision/detect`
- `GET /api/v1/vision/results/:id` → Vision Service `/vision/results/:id`
