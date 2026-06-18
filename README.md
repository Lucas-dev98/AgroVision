# 🌾 AgroVision - Plataforma Inteligente para Agricultura

**"Tecnologia inteligente para o campo"**

Plataforma unificada mobile e web para gestão completa da propriedade rural com inteligência artificial, visão computacional e entrada por voz. Suporta múltiplas culturas: café, pimenta, cacau, hortaliças, fruticultura, pecuária e agricultura familiar.

## 🎯 Público-Alvo

- Cafeicultores
- Produtores de pimenta-do-reino
- Cacauicultores
- Pecuaristas
- Produtores de hortaliças e fruticultura
- Pequenos e médios produtores rurais

## 🚀 Quick Start

### 1. Preparar Ambiente

```bash
# Clone o repositório
git clone https://github.com/seu-user/AgroVision.git
cd AgroVision

# Copie o arquivo de configuração
cp .env.example .env

# Configure variáveis de ambiente no .env
# DATABASE_URL, API_PORT, JWT_SECRET, etc
```

### 2. Iniciar Infraestrutura

```bash
# Com Docker Compose
docker-compose up -d

# Verificar status dos containers
docker-compose ps

# Ver logs
docker-compose logs -f postgres
```

Outputs esperados:
- **PostgreSQL:** `localhost:5432` (postgres:agrovision)
- **Redis:** `localhost:6379`
- **MinIO:** `localhost:9000` (minioadmin:minioadmin)
- **API Gateway:** `localhost:8080`
- **IA Service:** `localhost:8001`

### 3. Setup do Backend (Go)

```bash
# Entrar no diretório do API Gateway
cd services/api-gateway

# Instalar dependências
go mod download

# Executar testes
go test ./...

# Iniciar servidor (em desenvolvimento)
go run main.go
```

### 4. Setup do IA Service (Python)

```bash
# Entrar no diretório
cd services/ai-service

# Criar e ativar virtualenv
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar testes
pytest

# Iniciar servidor
python -m uvicorn app:app --reload
```

### 5. Setup do Frontend (Flutter)

```bash
# Entrar no diretório
cd frontend

# Instalar dependências
flutter pub get

# Executar em desenvolvimento (Web)
flutter run -d chrome

# Ou em Android/iOS
flutter run
```

### 6. Executar Testes Completos

```bash
# Na raiz do projeto
./run_all_tests.sh

# Ou manualmente
cd services/api-gateway && go test ./...
cd ../ai-service && pytest
cd ../../frontend && flutter test
```

### 3. Instalar Dependências Python

```bash
# Crie virtual environment
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale dependências compartilhadas
pip install -r shared/requirements.txt

# Instale dependências do animal-service
pip install -r services/animal-service/requirements.txt
```

### 4. Rodar Testes (TDD)

```bash
# Todos os testes
pytest

# Apenas Animal Service
pytest services/animal-service/

# Apenas converters
pytest shared/test_converters.py

# Com cobertura
pytest --cov

# Modo verbose
pytest -v

# Um teste específico
pytest services/animal-service/test_animal_repository.py::TestAnimalRepositoryCreate::test_create_animal_success -v
```---

## 📚 Documentação Completa

### Para Desenvolvedores
- 📖 [Guia Técnico de Implementação](docs/16_GUIA_TECNICO_IMPLEMENTACAO.md) — Padrões, schemas, APIs
- 🏗️ [Arquitetura de Microserviços](docs/02_ARQUITETURA.md) — Design system
- 🎯 [Especificação Completa](docs/15_AGROVISION_COMPLETA.md) — 12 módulos detalhados
- 📊 [Status do Projeto](STATUS.md) — Roadmap e progresso

### Para Usuários
- ✅ [TDD e Padrões](docs/06_TESTES_TDD.md) — Como escrever testes
- 🐳 [Setup Docker](docs/07_DOCKER_SETUP.md) — Containers
- 🔌 [Integração de APIs](docs/11_DOCKER_COMPOSE_GUIA.md) — External integrations

---

## 🎯 Os 12 Módulos

| # | Módulo | Status | Descrição |
|---|--------|--------|-----------|
| 1 | Cadastro da Propriedade | 🚀 MVP | Fazendas, talhões, GPS |
| 2 | Gestão da Produção | 🚀 MVP | Rastreamento por talhão |
| 3 | Calendário Agrícola | ⏳ Q3 | Planejamento automático |
| 4 | Controle Financeiro | 🚀 MVP | Custos e receitas |
| 5 | Gestão de Estoque | 🚀 MVP | Insumos, previsões |
| 6 | Clima Inteligente | 🚀 MVP | Alertas meteorológicos |
| 7 | Pragas e Doenças | ⏳ Q3 | Diagnóstico por IA |
| 8 | Visão Computacional | ⏳ Q3 | Análise de imagens |
| 9 | Assistente IA | 🚀 MVP | Chat contextualizado |
| 10 | Entrada por Voz | ⏳ Q3 | STT/TTS no campo |
| 11 | Dashboard Executivo | 🚀 MVP | KPIs em tempo real |
| 12 | Monitoramento por Drone | ⏳ Q4 | Análise aérea |

---

## 🏗️ Estrutura do Projeto

```
AgroVision/
├── frontend/                    # Flutter (mobile + web)
│   ├── lib/
│   │   ├── screens/            # Telas da app
│   │   ├── services/           # Chamadas de API
│   │   ├── providers/          # State management
│   │   └── models/             # DTOs
│   └── test/                   # Testes
│
├── services/                   # Microserviços
│   ├── api-gateway/            # Go - Autenticação, roteamento
│   ├── users-service/          # Go - Usuários e permissões
│   ├── property-service/       # Go - Propriedades e talhões
│   ├── production-service/     # Go - Produção
│   ├── financial-service/      # Go - Custos e receitas
│   ├── stock-service/          # Go - Estoque
│   ├── climate-service/        # Go - Integração climática
│   ├── reports-service/        # Go - Dashboard
│   ├── ai-service/             # Python - IA e NLP
│   ├── vision-service/         # Python - Visão computacional
│   └── ml-service/             # Python - Machine learning
│
├── infra/                      # Infraestrutura
│   ├── postgres/               # Migração de BD
│   ├── alembic/                # Versionamento de schema
│   └── docker-compose.yml      # Orquestração
│
├── shared/                     # Código compartilhado
│   ├── schemas.py              # DTOs compartilhados
│   └── requirements.txt        # Dependências Python
│
└── docs/                       # Documentação
    ├── 01_VISAO_DO_PRODUTO.md
    ├── 02_ARQUITETURA.md
    ├── 15_AGROVISION_COMPLETA.md
    ├── 16_GUIA_TECNICO_IMPLEMENTACAO.md
    └── ...
```

---

## 🔧 Tecnologias

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| **Frontend** | Flutter | Um código para Web, Android, iOS |
| **Backend Principal** | Go | Performance, concorrência, escalabilidade |
| **IA e ML** | Python | Ecossistema ML, TensorFlow, scikit-learn |
| **Banco Dados** | PostgreSQL | Relacional, confiável, extensível |
| **Cache** | Redis | Cache, sessões, filas |
| **Armazenamento** | MinIO | S3 compatível, self-hosted |
| **Containers** | Docker | Padronização, reproducibilidade |
| **Orquestração** | Kubernetes | Escala futura |

---

## 🚀 Roadmap

### Q2 2026 (MVP)
- [x] Definição de produto
- [ ] Implementação dos 7 módulos MVP
- [ ] Testes beta com 50 usuários
- [ ] Iteração baseada em feedback

### Q3 2026
- [ ] Módulos 8, 9, 10 (Calendário, Pragas, Voz)
- [ ] Suporte a 3 culturas
- [ ] 200+ usuários

### Q4 2026
- [ ] Visão computacional avançada
- [ ] Integração com drones
- [ ] Suporte a pecuária

### 2027
- [ ] Kubernetes
- [ ] Marketplace
- [ ] API pública

---

## 📞 Contribuição

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para como colaborar.

## 📄 Licença

MIT License - veja [LICENSE.md](LICENSE.md)
        self.db.commit()
        self.db.refresh(animal)
        return animal
```

**Status**: ✅ PASSA

#### Fase 3️⃣: REFACTOR (Melhorar)

```python
# Adicionar logging, validações extras, otimizações
```

---

## 🏗️ Estrutura do Projeto

```
boi/
├── docker-compose.yml          # Infraestrutura local
├── pytest.ini                  # Config pytest
├── .env.example                # Variáveis de ambiente
│
├── shared/                     # Código compartilhado
│   ├── __init__.py
│   ├── schemas.py              # DTOs Pydantic
│   ├── converters.py           # Conversões (kg ↔ arrobas)
│   ├── database.py             # SQLAlchemy config
│   ├── test_converters.py      # Testes converters
│   └── requirements.txt
│
├── services/
│   └── animal-service/         # Serviço de Animais
│       ├── main.py             # Entry point
│       ├── app.py              # FastAPI app
│       ├── models.py           # SQLAlchemy models (ORM)
│       ├── repository.py       # Data access layer
│       ├── conftest.py         # Fixtures pytest
│       ├── test_animal_repository.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── infra/
│   └── postgres/
│       └── init.sql            # Schema inicial
│
└── PLANEJAMENTO.md             # Documentação completa
```

---

## 🧪 Entendendo os Testes

### Estrutura de um Teste

```python
def test_create_animal_success(animal_repository, animal_create_dto):
    """
    GIVEN: DTO válido para criar animal       ← Contexto
    WHEN: Chamar repository.create()          ← Ação
    THEN: Deve retornar AnimalModel com ID    ← Resultado esperado
    """
    # Arrange (Preparar)
    # ... dados já preparados via fixtures ...
    
    # Act (Executar)
    animal = animal_repository.create(animal_create_dto)
    
    # Assert (Validar)
    assert animal.id is not None
    assert animal.ear_tag == "001"
```

### Fixtures (Dados Reutilizáveis)

```python
# conftest.py
@pytest.fixture
def animal_create_dto():
    """Dados para criar animal - reusável em todos os testes"""
    return AnimalCreate(
        ear_tag="001",
        name="Bessie",
        breed="Nelore",
        gender="F"
    )

# teste
def test_algo(animal_create_dto):  # Fixture é injetada automaticamente
    assert animal_create_dto.breed == "Nelore"
```

### Banco de Dados de Teste

```python
# conftest.py usa SQLite em memória (rápido, isolado)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db(engine):
    """Cada teste roda em transação isolada - rollback ao fim"""
    # ... transação inicia ...
    yield session
    # ... rollback automático ...
```

---

## 📊 Testes Implementados

### ✅ Animal Repository (50+ testes)
- ✓ Create (com dados válidos, minimal, duplicata)
- ✓ Read (por ID, ear_tag, listar, buscar)
- ✓ Update (atualizar fields, validar imutáveis)
- ✓ Delete (soft delete mudando status)
- ✓ Agregações (count, filter by breed, status)

### ✅ Converters (20+ testes)
- ✓ kg ↔ arrobas bidirecionais
- ✓ Cálculo de valor (peso × preço)
- ✓ Ganho de peso
- ✓ Ganho diário
- ✓ Validação de valores (negativos devem falhar)

---

## 🔄 Workflow Desenvolvimento

### Adicionar Nova Feature (TDD)

```
1. Escrever teste que FALHA
   pytest services/animal-service/ -v

2. Implementar código mínimo para passar
   pytest services/animal-service/ -v

3. Refatorar/melhorar
   pytest services/animal-service/ -v

4. Commit quando tudo passa
   git add . && git commit -m "feat: nova feature"
```

### Exemplo: Adicionar filtro por gender

```python
# 1️⃣ RED - Escrever teste
def test_list_animals_by_gender(animal_repository, created_animal):
    animals = animal_repository.list_by_gender("F")
    assert len(animals) == 1
    assert animals[0].gender == "F"

# 2️⃣ GREEN - Implementar
def list_by_gender(self, gender: str):
    return self.db.query(AnimalModel).filter(
        AnimalModel.gender == gender
    ).all()

# 3️⃣ REFACTOR - Melhorar
# ... otimizar query, adicionar documentação ...
```

---

## 🛠️ SQLAlchemy ORM Basics

### Criar (Create)

```python
from services.animal_service.models import AnimalModel
from shared.schemas import AnimalCreate
from shared.database import SessionLocal

animal_data = AnimalCreate(breed="Nelore", gender="F")
animal = AnimalModel(**animal_data.model_dump())
db.add(animal)
db.commit()
```

### Ler (Read)

```python
# Por ID
animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()

# Todos
animals = db.query(AnimalModel).all()

# Com filtro
active = db.query(AnimalModel).filter(AnimalModel.status == "active").all()
```

### Atualizar (Update)

```python
animal = db.query(AnimalModel).filter(AnimalModel.id == animal_id).first()
animal.name = "Novo Nome"
db.commit()
db.refresh(animal)
```

### Deletar (Delete)

```python
db.query(AnimalModel).filter(AnimalModel.id == animal_id).delete()
db.commit()
```

---

## 🔗 Conversão de Unidades

```python
from shared.converters import kg_to_arrobas, calculate_animal_value

# Converter 450 kg para arrobas
arrobas = kg_to_arrobas(450)  # 30.0

# Calcular valor: 30 arrobas × R$ 367,05
valor = calculate_animal_value(30, 367.05)  # R$ 11.011,50
```

---

## 📝 Próximos Passos

Após confirm que os testes passam:

1. **Criar endpoints FastAPI** para Animal Service
2. **Implementar Weighing Service** (integração balança)
3. **Health Service** (controle de vacinas)
4. **Vision Service** (YOLO)
5. **Market Service** (CEPEA)

---

## 🐛 Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'shared'`

```bash
# Adicione no PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou edite conftest.py
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

### Erro: `psycopg2` connection refused

```bash
# Verifique se PostgreSQL está rodando
docker-compose ps

# Reinicie
docker-compose down && docker-compose up
```

### Testes falhando com "database is locked"

```bash
# Use SQLite com timeout
engine = create_engine(DATABASE_URL, 
    connect_args={"timeout": 30})
```

---

## 📖 Referências

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pytest Documentation](https://docs.pytest.org/)
- [TDD Best Practices](https://en.wikipedia.org/wiki/Test-driven_development)

---

**Status do Projeto**: 🟡 Em Desenvolvimento (Animal Service v1.0)

Última atualização: 15/04/2026
