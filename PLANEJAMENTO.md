# SISTEMA DE GESTÃO DE REBANHO - PLANEJAMENTO COMPLETO

## 📋 VISÃO GERAL DO PROJETO

**Objetivo**: Sistema inteligente de gestão de rebanho para fazenda de 17 alqueiros utilizando:
- Visão Computacional (YOLO)
- Integração com Sistemas de Pesagem
- Cotações em Tempo Real (CEPEA)
- Controle Alimentar, Sanitário e Produtivo

---

## 🏗️ ARQUITETURA GERAL

### Visão De Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Vue)                    │
│            Dashboard, Relatórios, Monitoramento             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                    │
│              Roteamento, Autenticação, Rate Limit           │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────────┐
        │         MICROSERVIÇOS (FastAPI)             │
        ├─────────────────────────────────────────────┤
        │ ├─ Animal Service                           │
        │ ├─ Nutrition Service                        │
        │ ├─ Health Service                           │
        │ ├─ Weighing Service                         │
        │ ├─ Vision Service (YOLO)                    │
        │ └─ Market Service (CEPEA)                   │
        └─────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────────┐
        │         CAMADA DE DADOS                     │
        ├─────────────────────────────────────────────┤
        │ ├─ PostgreSQL (Dados Estruturados)          │
        │ ├─ MongoDB (Históricos + Telemetria)        │
        │ ├─ Redis (Cache + Queue)                    │
        │ └─ MinIO (Imagens/Vídeos YOLO)              │
        └─────────────────────────────────────────────┘
```

---

## 🗄️ BANCOS DE DADOS

### Resposta: SIM, DOIS BANCOS PRINCIPAIS

#### 1. **PostgreSQL** (Dados Transacionais)
- Estruturado, ACID, relações claras
- Animais, Propriedades, Vacinas, Usuários, Configurações

#### 2. **MongoDB** (Dados Não-Estruturados)
- Históricos de pesagem, eventos, telemetria
- Logs de câmera, detecções YOLO
- Flexibilidade para dados variáveis

#### 3. **Redis** (Cache + Sessões)
- Cotações CEPEA em cache
- Sessões de usuário
- Filas de processamento

#### 4. **MinIO/S3** (Armazenamento de Arquivos)
- Imagens/vídeos das câmeras
- Modelos YOLO treinados

---

## 🔧 ESTRUTURA DE MICROSERVIÇOS

### 1. **Animal Service** - Gerenciamento de Animais

**Responsabilidades**:
- CRUD de animais (ID único, raça, características)
- Histórico médico-produtivo
- Identificação por YOLO + Tags
- Filiação (mãe, pai)

**Banco**: PostgreSQL + MongoDB (histórico)

**Endpoints Principais**:
```
POST   /animals - Registrar novo animal
GET    /animals/{id} - Detalhes do animal
PUT    /animals/{id} - Atualizar dados
DELETE /animals/{id} - Remover animal
GET    /animals - Listar com filtros (rebanho, status)
```

---

### 2. **Weighing Service** - Sistema de Pesagem

**Responsabilidades**:
- Integração com balança (RS-232/TCP/IP)
- Conversão kg → arrobas (1 arroba = 15 kg)
- Histórico de pesador
- Alertas de variação de peso

**Banco**: PostgreSQL (registro) + MongoDB (telemetria)

**Endpoints Principais**:
```
POST   /weighing/capture - Capturar peso da balança
GET    /weighing/animal/{animal_id} - Histórico de peso
POST   /weighing/convert - Converter kg/arroba
GET    /weighing/stats/{animal_id} - Estatísticas
```

**Integração Balança**:
```python
# Exemplo: Conexão com balança via SerialPort
class BalanceConnector:
    - Ler peso (byte serial)
    - Validar checksum
    - Converter formato
    - Associar animal (RFID ou manual)
```

---

### 3. **Health Service** - Controle Sanitário

**Responsabilidades**:
- Registro de vacinas (tipo, data, validade)
- Tratamentos veterinários
- Alertas de revacina
- Relatórios sanitários

**Banco**: PostgreSQL

**Endpoints Principais**:
```
POST   /health/vaccines - Registrar vacina
GET    /health/animal/{animal_id}/vaccines - Histórico vacinal
POST   /health/alert - Criar alerta (revacina)
GET    /health/alerts - Alertas pendentes
```

---

### 4. **Nutrition Service** - Controle Alimentar

**Responsabilidades**:
- Registro de ingestão alimentar
- Cálculo de nutrientes
- Previsão de consumo
- Otimização de ração

**Banco**: PostgreSQL + MongoDB (histórico detalhado)

**Endpoints Principais**:
```
POST   /nutrition/feed - Registrar alimentação
GET    /nutrition/animal/{animal_id} - Histórico alimentar
POST   /nutrition/calculate - Calcular nutrientes
GET    /nutrition/forecast - Previsão de consumo
```

---

### 5. **Vision Service** - Processamento YOLO

**Responsabilidades**:
- Receber frames de câmeras IP
- Detectar animais com YOLO
- Classificar trough (vazio/cheio)
- Identificar animal
- Armazenar detecções

**Banco**: MongoDB + MinIO

**Endpoints Principais**:
```
POST   /vision/detect - Processar frame
GET    /vision/animals - Animais detectados
GET    /vision/troughs - Status dos cochos
GET    /vision/history/{animal_id} - Histórico detecção
```

---

### 6. **Market Service** - Cotações CEPEA

**Responsabilidades**:
- Consumir API CEPEA de forma agendada
- Armazenar cotações históricas
- Calcular projeção de valor
- Fornecer cotação atual

**Banco**: PostgreSQL + Redis (cache)

**Endpoints Principais**:
```
GET    /market/current - Cotação atual (boi gordo)
GET    /market/history - Histórico de cotações
GET    /market/projected-value/{animal_id} - Valor projetado
GET    /market/list - Todas cotações (café, soja, etc)
```

**Detalhes CEPEA**:
```
- Endpoint Base: https://cepea.org.br/br/indicador/boi-gordo.aspx
- Cotação: R$367,05/arroba (14/04/2026)
- Frequência Update: Diária (dias úteis)
- Conversão: Valor em R$ × Peso em arrobas
- Variação Regional: Considerar estado (SP base)
```

---

## 📊 ESQUEMA DO BANCO DE DADOS

### PostgreSQL - Tabelas Principais

```sql
-- Animais
CREATE TABLE animals (
    id UUID PRIMARY KEY,
    ear_tag VARCHAR(20) UNIQUE,
    name VARCHAR(100),
    breed VARCHAR(50),
    birth_date DATE,
    gender CHAR(1),
    status ENUM('active', 'sold', 'dead'),
    mother_id UUID REFERENCES animals(id),
    father_id UUID REFERENCES animals(id),
    detected_by_yolo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Pesagens
CREATE TABLE weighing_records (
    id UUID PRIMARY KEY,
    animal_id UUID REFERENCES animals(id),
    weight_kg DECIMAL(8,2),
    weight_arrobas DECIMAL(8,2),
    recorded_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vacinas
CREATE TABLE vaccines (
    id UUID PRIMARY KEY,
    animal_id UUID REFERENCES animals(id),
    vaccine_name VARCHAR(100),
    application_date DATE,
    next_dose_date DATE,
    veterinarian VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alimentação
CREATE TABLE feeding_records (
    id UUID PRIMARY KEY,
    animal_id UUID REFERENCES animals(id),
    feed_type VARCHAR(100),
    quantity_kg DECIMAL(8,2),
    fed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cotações
CREATE TABLE cattle_prices (
    id UUID PRIMARY KEY,
    indicator_type VARCHAR(50), -- 'fat_cattle', 'calf', etc
    price_per_arroba DECIMAL(10,2),
    currency VARCHAR(3), -- 'BRL', 'USD'
    date DATE UNIQUE,
    daily_change DECIMAL(5,2),
    monthly_change DECIMAL(5,2),
    source VARCHAR(50), -- 'CEPEA'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Usuários
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    name VARCHAR(100),
    role ENUM('admin', 'operator', 'viewer'),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Configurações
CREATE TABLE settings (
    id UUID PRIMARY KEY,
    farm_name VARCHAR(100),
    farm_size_alqueires INT,
    location VARCHAR(100),
    currency_default VARCHAR(3),
    arroba_kg DECIMAL(5,2), -- 15 por padrão
    created_at TIMESTAMP DEFAULT NOW()
);
```

### MongoDB - Coleções (Variáveis/Históricas)

```javascript
// vision_detections
{
    _id: ObjectId,
    animal_id: UUID,
    timestamp: ISODate,
    confidence: 0.95,
    bounding_box: { x, y, width, height },
    trough_status: 'empty' | 'partial' | 'full',
    image_path: 'path/to/image.jpg',
    camera_id: 'cam_01'
}

// weighing_telemetry
{
    _id: ObjectId,
    weighing_record_id: UUID,
    raw_bytes: 'hex_string',
    balance_id: 'balance_001',
    signal_strength: 95,
    timestamp: ISODate
}

// events_log
{
    _id: ObjectId,
    event_type: 'animal_detected' | 'weight_recorded' | 'vaccine_applied',
    entity_id: UUID,
    details: {},
    timestamp: ISODate,
    user_id: UUID
}
```

---

## 🚀 ARQUITETURA DE MICROSERVIÇOS (Estrutura de Pastas)

```
projeto-gado/
├── docker-compose.yml          # Orquestração local
├── README.md
├── .env.example
│
├── api-gateway/                # FastAPI Gateway
│   ├── main.py
│   ├── middleware/
│   └── requirements.txt
│
├── services/
│   │
│   ├── animal-service/
│   │   ├── main.py
│   │   ├── app.py
│   │   ├── models/
│   │   │   ├── animal.py
│   │   │   └── schemas.py
│   │   ├── repository/
│   │   │   └── animal_repository.py
│   │   ├── tests/
│   │   │   ├── test_animal_service.py
│   │   │   └── conftest.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── weighing-service/
│   │   ├── main.py
│   │   ├── app.py
│   │   ├── integrations/
│   │   │   └── balance_connector.py
│   │   ├── models/
│   │   ├── repository/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── health-service/
│   │   ├── main.py
│   │   ├── app.py
│   │   ├── models/
│   │   ├── repository/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── nutrition-service/
│   │   ├── main.py
│   │   ├── app.py
│   │   ├── models/
│   │   ├── repository/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── vision-service/
│   │   ├── main.py
│   │   ├── app.py
│   │   ├── yolo/
│   │   │   ├── detector.py
│   │   │   ├── trough_classifier.py
│   │   │   └── models/
│   │   ├── integrations/
│   │   │   └── camera_handler.py
│   │   ├── repository/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── market-service/
│       ├── main.py
│       ├── app.py
│       ├── integrations/
│       │   └── cepea_client.py
│       ├── models/
│       ├── repository/
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
│
├── shared/
│   ├── models/
│   │   ├── base.py
│   │   └── enums.py
│   ├── utils/
│   │   ├── database.py
│   │   ├── cache.py
│   │   └── converters.py
│   └── requirements.txt
│
└── infra/
    ├── postgres/
    │   ├── init.sql
    │   └── Dockerfile
    ├── mongodb/
    │   └── docker-compose.override.yml
    ├── redis/
    │   └── redis.conf
    └── minio/
        └── docker-compose.override.yml
```

---

## 🧪 METODOLOGIA TDD

### Estrutura de Testes

```
tests/
├── unit/
│   ├── test_animal_service.py
│   ├── test_weighing_service.py
│   ├── test_converters.py
│   └── ...
│
├── integration/
│   ├── test_animal_api.py
│   ├── test_weighing_api.py
│   └── ...
│
└── fixtures/
    ├── animals.json
    ├── weights.json
    └── conftest.py
```

### Exemplo Teste Unitário (TDD)

```python
# tests/unit/test_animal_service.py
import pytest
from uuid import uuid4
from services.animal_service.models import Animal

@pytest.fixture
def animal_data():
    return {
        "ear_tag": "001",
        "name": "Bessie",
        "breed": "Nelore",
        "gender": "F"
    }

def test_create_animal(animal_data):
    """Test crear animal com dados válidos"""
    animal = Animal(**animal_data)
    assert animal.ear_tag == "001"
    assert animal.status == "active"

def test_weight_conversion():
    """Test conversão kg para arrobas"""
    from shared.utils.converters import kg_to_arrobas
    
    result = kg_to_arrobas(450)
    assert result == 30.0  # 450 / 15 = 30

def test_calculate_animal_value():
    """Test cálculo valor animal"""
    from services.market_service.calculator import calculate_value
    
    weight_arrobas = 30
    price_per_arroba = 367.05
    
    value = calculate_value(weight_arrobas, price_per_arroba)
    assert value == pytest.approx(11011.5)
```

---

## 🔄 FLUXO DE DADOS PRINCIPAL

### Caso de Uso: Pesagem e Cálculo de Valor

```
1. Animal entra em pé na balança
2. Balança lê peso via SerialPort → Weighing Service
3. Weighing Service:
   - Associa peso ao animal (RFID/manual)
   - Valida dados
   - Converte kg → arrobas
   - Armazena em PostgreSQL
   - Registra telemetria em MongoDB
4. Market Service consulta cotação CEPEA atual
5. Dashboard exibe:
   - Peso: 450 kg (30 arrobas)
   - Valor por arroba: R$ 367,05
   - Valor total: R$ 11.011,50
   - Variação desde última pesagem
```

---

## 💾 DEPENDÊNCIAS PRINCIPAIS

### Backend
```
fastapi==0.109.0
sqlalchemy==2+
psycopg2-binary==2.9+
pymongo==4.0+
redis==5.0+
pydantic==2.0+
python-dotenv==1.0+
```

### Visão Computacional
```
yolov8==8.0+
opencv-python==4.8+
pillow==10.0+
torch==2.0+
```

### Integração
```
requests==2.31+
aiohttp==3.9+
minio==7.0+
```

### Testes
```
pytest==7.4+
pytest-asyncio==0.21+
pytest-cov==4.1+
httpx==0.25+
```

---

## 📅 PRÓXIMOS PASSOS (FASE 1: SETUP)

### Sprint 1: Infraestrutura (Semana 1-2)
- [ ] Configurar PostgreSQL + Migrations
- [ ] Configurar MongoDB
- [ ] Configurar Redis
- [ ] Docker Compose local
- [ ] Estrutura de pastas
- [ ] CI/CD Pipeline básico

### Sprint 2: Animal Service (Semana 3-4)
- [ ] Modelos Pydantic
- [ ] Testes unitários (TDD)
- [ ] Repositório + ORM
- [ ] Endpoints CRUD
- [ ] Testes integração

### Sprint 3: Weighing Service (Semana 5-6)
- [ ] Integração balança (simular)
- [ ] Conversão kg/arrobas
- [ ] Endpoints de pesagem
- [ ] Testes completos

### Sprint 4: Market Service (Semana 7)
- [ ] API CEPEA wrapper
- [ ] Scraping/caching cotações
- [ ] Endpoints de mercado
- [ ] Cálculo de valor

### Sprint 5: Vision Service (Semana 8-9)
- [ ] Modelo YOLO download
- [ ] Detector de animais
- [ ] Classificador trough
- [ ] Endpoints vision

### Sprint 6: Integração (Semana 10+)
- [ ] API Gateway
- [ ] Autenticação JWT
- [ ] Frontend inicial
- [ ] Deploy

---

## ⚙️ VARIAÇÕES DE ARROBA (INFORMAÇÃO IMPORTANTE)

A **arroba** é uma unidade regional:
- **Brasil (padrão)**: 1 arroba = 15 kg
- **Alguns estados**: 1 arroba = 14,688 kg (histórico)
- **Sistema recomendado**: Usar 15 kg como padrão, com campo configurável

### Configuração no Sistema:

```python
# settings table / environment
ARROBA_IN_KG = 15.0  # Configurável por região/estado
```

---

## 🔐 Integração CEPEA - Detalhes

### Endpoint Recomendado
```
GET https://cepea.org.br/br/indicador/boi-gordo.aspx
```

**Alternativa**: Usar API interna (verificar com CEPEA)

### Dados Capturados
- Data da cotação
- Preço por arroba (R$/arroba - 15 kg)
- Variação diária (%)
- Variação mensal (%)
- Preço em dólar

### Agendamento
```python
# Atualizar cotação diariamente às 10h
@scheduler.scheduled_job('cron', hour=10, minute=0)
async def update_cattle_prices():
    # Fetch CEPEA data
    # Atualizar banco
```

---

## ✅ RESUMO EXECUTIVO

| Aspecto | Decisão |
|---------|---------|
| **Backend** | FastAPI (async, moderno) |
| **Banco Principal** | PostgreSQL (ACID + Estruturado) |
| **Banco Secundário** | MongoDB (Históricos/Telemetria) |
| **Cache** | Redis |
| **Arquitetura** | Microserviços (6 serviços) |
| **Metodologia** | TDD + Pytest |
| **Deploy** | Docker + Docker Compose |
| **Visão Computacional** | YOLOv8 |

---

## 🎯 PRIMEIRO PASSO RECOMENDADO

**Comece por**: **Animal Service com TDD**

Por quê?
1. Não depende de outros serviços
2. Base para todo sistema
3. Aprende padrões (TDD, ORM, API)
4. Rápido validar conceito

**Próximo**: Agora vamos para o código! 🚀
