# 🧠 Arquitetura Geral (Microserviços)

## Diagrama em Camadas

```
┌─────────────────────────────────────────────────────────┐
│              Frontend Layer (React Dashboard)            │
│              - Gráficos de peso                          │
│              - KPIs de ganho/valor                       │
│              - Alertas sanitários                        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│         API Gateway (FastAPI)                           │
│         - Autenticação JWT                              │
│         - Rate Limiting                                 │
│         - Roteamento                                    │
│         - Agregação de dados                            │
└────────────────────┬────────────────────────────────────┘
       ┌─────────────┼─────────────┬──────────────────┐
       │             │             │                  │
┌──────▼──┐   ┌─────▼────┐  ┌────▼─────┐  ┌────────▼──────┐
│ animal- │   │ pesagem- │  │alimentação│  │    sanidade-  │
│ service │   │ service  │  │ service   │  │    service    │
└──────┬──┘   └─────┬────┘  └────┬─────┘  └────────┬──────┘
       │             │            │                 │
       └─────────────┼────────────┴─────────────────┘
                     │
       ┌─────────────┼──────────────────────┐
       │             │                      │
┌──────▼──┐   ┌─────▼────┐   ┌────────────▼────┐
│ cotacao-│   │ analytics-│   │edge-services    │
│ service │   │ service  │   │(ingestion+vision)│
└─────────┘   └──────────┘   └─────────────────┘
       │             │                │
       └─────────────┼────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│       PostgreSQL Database (Single DB, Logical Split)    │
│  - animais                                              │
│  - pesagens                                             │
│  - alimentacao                                          │
│  - vacinas                                              │
│  - cotacao_arroba                                       │
│  - alertas                                              │
└─────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│         Hardware Layer (Edge)                           │
│  - Balança (Serial/USB)                                │
│  - RFID                                                 │
│  - Câmeras IP (RTSP)                                    │
│  - CoioPi/IoT Gateways                                  │
└─────────────────────────────────────────────────────────┘
```

## Fluxo de Dados

### Pesagem
```
Balança (Serial) 
  → ingestion-service 
  → pesagem-service 
  → PostgreSQL
  → analytics-service
  → Dashboard
```

### Monitoramento Alimentar
```
Câmera IP (RTSP)
  → vision-service (YOLO)
  → alimentacao-service
  → PostgreSQL
  → analytics-service
  → Dashboard
```

### Cotação
```
CEPEA (Web)
  → cotacao-service (Scraper)
  → PostgreSQL
  → analytics-service (Cálculo de valor)
  → Dashboard
```

## Comunicação entre Serviços

- **Síncrona**: HTTP REST (FastAPI)
- **Assíncrona**: Redis Queue (futuro) / RabbitMQ (futuro)
- **Banco**: PostgreSQL compartilhado com tabelas isoladas

## Isolamento de Contexto

Cada serviço é responsável por suas tabelas:
- `animal-service` → `animais`
- `pesagem-service` → `pesagens`
- `alimentacao-service` → `alimentacao`
- `sanidade-service` → `vacinas`
- `cotacao-service` → `cotacao_arroba`
- `analytics-service` → `alertas` (read-only dos outros)
