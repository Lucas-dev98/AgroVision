# Vision & ML Services - Quick Start

Guia rápido para iniciar os serviços de Vision (YOLO) e ML (Machine Learning).

## 🚀 Iniciar com Docker Compose

```bash
cd /home/lucasbastos/AgroVision

# Iniciar todos os serviços (including Vision e ML)
docker-compose -f docker-compose.go.yml up -d

# Ver logs
docker-compose -f docker-compose.go.yml logs -f vision-service
docker-compose -f docker-compose.go.yml logs -f ml-service
docker-compose -f docker-compose.go.yml logs -f api-gateway
```

## 🏗️ Iniciar Serviços Individualmente

### Vision Service

```bash
cd services/vision_service_go
go mod download
go run ./cmd/main/main.go
# Ou: go build -o vision-service ./cmd/main && ./vision-service
```

Endpoint local: `http://localhost:8003`
Via API Gateway: `http://localhost:9000/api/v1/vision/detect`

### ML Service

```bash
cd services/ml_service_go
go mod download
go run ./cmd/main/main.go
# Ou: go build -o ml-service ./cmd/main && ./ml-service
```

Endpoint local: `http://localhost:8004`
Via API Gateway: `http://localhost:9000/api/v1/ml/models`

## 📋 Portas

| Serviço | Porta Local | Docker | Gateway |
|---------|-------------|--------|---------|
| Vision | 8003 | 8103 | /api/v1/vision |
| ML | 8004 | 8104 | /api/v1/ml |
| API Gateway | 8080 | 9000 | - |

## 🧪 Testar Endpoints

### Vision - Detectar Animais

```bash
# Fazer upload de imagem
curl -X POST -F "image=@photo.jpg" \
  http://localhost:9000/api/v1/vision/detect \
  -H "Authorization: Bearer YOUR_TOKEN"

# Listar resultados
curl http://localhost:9000/api/v1/vision/results \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### ML - Listar Modelos

```bash
curl http://localhost:9000/api/v1/ml/models \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### ML - Fazer Treinamento

```bash
curl -X POST http://localhost:9000/api/v1/ml/train \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "model_1",
    "epochs": 10,
    "batch_size": 32,
    "learning_rate": 0.001
  }'
```

### ML - Fazer Predição

```bash
curl -X POST http://localhost:9000/api/v1/ml/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "model_1",
    "input": "dados de entrada"
  }'
```

## 🔗 Frontend Integration

O frontend em `http://localhost:5173` já está configurado para chamar esses endpoints via `apiService.ts`:

- Vision Page (detecção de animais): `/vision` route
- ML Page (treinamento e predição): `/ml` route

## 📚 Documentação Completa

- [Vision Service README](services/vision_service_go/README.md)
- [ML Service README](services/ml_service_go/README.md)

## 🐛 Troubleshooting

### Serviço não inicia

```bash
# Verificar se porta está em uso
lsof -i :8003
lsof -i :8004

# Limpar containers antigos
docker-compose -f docker-compose.go.yml down
docker system prune -f
```

### API Gateway não consegue conectar aos serviços

```bash
# Verificar se os serviços estão rodando
docker-compose -f docker-compose.go.yml ps

# Verificar logs do gateway
docker-compose -f docker-compose.go.yml logs api-gateway
```

### Erro de compilação Go

```bash
# Limpar cache e reinstalar dependencies
go clean -modcache
go mod download

# Atualizar go.mod se necessário
go mod tidy
```

## 💡 Próximas Etapas

1. **Integrar YOLO Real**: Substituir simulação em Vision Service por modelo YOLO real
2. **Implementar ML Frameworks**: Integrar TensorFlow/PyTorch ao ML Service
3. **Persistência**: Adicionar banco de dados (MongoDB) para armazenar resultados
4. **Autenticação**: Adicionar validação JWT nos serviços individuais
5. **Monitoramento**: Adicionar métricas Prometheus/Grafana
