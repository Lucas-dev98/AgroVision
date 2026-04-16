# 🧩 Microserviços - Responsabilidades

## 🔌 3.1 ingestion-service (IoT)

**Responsável por hardware**

### Funções
- Ler balança (serial)
- Ler RFID
- Enviar eventos para fila

### Evento Padrão
```json
{
  "tipo": "pesagem",
  "animal_id": 10,
  "peso": 450,
  "timestamp": "2026-04-15T10:30:00Z",
  "rfid": "animal_001"
}
```

### Stack
- Python + FastAPI
- PySerial (balança)
- asyncio (event loop)

---

## 📸 3.2 vision-service

**IA com YOLO para visão computacional**

### Funções
- Detectar vacas no vídeo
- Identificar presença no cocho
- Estimar comportamento
- Classificar estado (comendo, bebendo, deitado)

### Output Padrão
```json
{
  "tipo": "visao",
  "animal_ids": [1, 2, 3],
  "comportamento": "comendo",
  "timestamp": "2026-04-15T10:30:00Z",
  "confianca": 0.95
}
```

### Stack
- Python + FastAPI
- YOLO v8
- OpenCV
- RTSP stream

---

## 🌐 3.3 api-gateway

**Ponto único de entrada**

### Funções
- Autenticação (JWT)
- Roteamento para microserviços
- Agregação de dados
- Rate limiting
- Logging

### Endpoints
- `POST /auth/login`
- `GET /animals`
- `POST /pesagens`
- `GET /pesagens/{animal_id}`
- Etc...

### Stack
- FastAPI
- JWT (python-jose)
- AsyncIO

---

## 🐂 3.4 animal-service

**Gestão do rebanho**

### Responsabilidades
- Cadastro de animais
- Raça, idade, lote
- Vínculo com RFID
- Status (ativo, vendido, falecido)
- Histórico

### Tabelas
- `animais`
- `lotes`

### Endpoints
- `POST /animals` — Cadastrar
- `GET /animals` — Listar
- `GET /animals/{id}` — Detalhe
- `PUT /animals/{id}` — Atualizar
- `DELETE /animals/{id}` — Remover

### Stack
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (schemas)

---

## ⚖️ 3.5 pesagem-service

**Core do sistema de pesar**

### Responsabilidades
- Registrar pesagem
- Calcular arroba (peso ÷ 15)
- Calcular valor (arroba × cotação)
- Histórico por animal
- Alertas de ganho/perda

### Tabelas
- `pesagens`

### Cálculos
```python
def calcular_arroba(peso_kg: float) -> float:
    return peso_kg / 15

def calcular_valor(arroba: float, preco_arroba: float) -> float:
    return arroba * preco_arroba

def ganho_diario(peso_hoje: float, peso_ontem: float) -> float:
    return peso_hoje - peso_ontem
```

### Endpoints
- `POST /pesagens` — Registrar
- `GET /pesagens/{animal_id}` — Histórico
- `GET /pesagens/{animal_id}/ultima` — Última pesagem
- `GET /pesagens/{animal_id}/ganho` — Ganho acumulado

### Stack
- FastAPI
- SQLAlchemy
- Decimal (precisão)

---

## 🥣 3.6 alimentacao-service

**Monitoramento alimentar**

### Responsabilidades
- Tempo no cocho
- Frequência de visitas
- Ingestão estimada
- Alertas de não-alimentação

### Tabelas
- `alimentacao`

### Métricas
```python
def tempo_total_cocho(animal_id: int, data: date) -> timedelta:
    # Soma de tempo_saída - tempo_entrada

def frequencia_diaria(animal_id: int, data: date) -> int:
    # Contagem de visitas ao cocho
```

### Endpoints
- `POST /alimentacao` — Registrar evento
- `GET /alimentacao/{animal_id}/dia` — Dia
- `GET /alimentacao/{animal_id}/semana` — Semana
- `GET /alimentacao/{animal_id}/alertas` — Alertas

### Stack
- FastAPI
- SQLAlchemy
- Trigonometria (câmera)

---

## 💉 3.7 sanidade-service

**Controle sanitário**

### Responsabilidades
- Registrar vacinas
- Histórico de doenças
- Alertas de próxima dose
- Isolamento de animais

### Tabelas
- `vacinas`
- `doencas`
- `isolamento`

### Endpoints
- `POST /vacinas` — Registrar
- `GET /vacinas/{animal_id}` — Histórico
- `GET /vacinas/alertas` — Próximas doses
- `POST /isolamento` — Isolar animal

### Stack
- FastAPI
- SQLAlchemy

---

## 💰 3.8 cotacao-service

**Integração com CEPEA**

### Responsabilidades
- Scraping diário de CEPEA
- Armazenar histórico
- Fornecer preço atual
- Alertas de variação

### Tabelas
- `cotacao_arroba`

### Webhook
```json
{
  "data": "2026-04-15",
  "preco": 280.50,
  "fonte": "CEPEA",
  "variacao": 2.5
}
```

### Endpoints
- `GET /cotacao/atual` — Preço hoje
- `GET /cotacao/historico` — Últimos 30 dias
- `GET /cotacao/media` — Média mensal

### Stack
- FastAPI
- BeautifulSoup (scraping)
- Celery (job diário) ou APScheduler

---

## 📊 3.9 analytics-service

**BI e inteligência**

### Responsabilidades
- Ganho de peso por animal
- Consumo alimentar
- Valor total do rebanho
- Alertas inteligentes
- Dashboard queries

### Queries Principais
```python
def ganho_medio_rebanho(lote_id: int, periodo: int) -> float:
    # Ganho médio por animal

def valor_total_rebanho() -> float:
    # Σ (arroba * cotação)

def alerta_saude_rebanho() -> List[AlertaType]:
    # Animais com alertas de saúde

def eficiencia_alimentacao(animal_id: int) -> float:
    # Ganho / consumo
```

### Endpoints
- `GET /analytics/rebanho` — KPIs gerais
- `GET /analytics/animal/{id}` — Dados individuais
- `GET /analytics/alertas` — Lista de alertas
- `GET /analytics/previsoes` — ML (futuro)

### Stack
- FastAPI
- Pandas (análise)
- Scikit-learn (ML futuro)
