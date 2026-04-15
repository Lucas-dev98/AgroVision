# 🐄 Sistema de Gestão de Rebanho - Gado

Sistema inteligente de gerenciamento de rebanho para fazenda com visão computacional (YOLO), integração com balança, cotações de mercado e controle sanitário/nutricional.

## 🚀 Quick Start

### 1. Preparar Ambiente

```bash
# Clone/entre no diretório
cd boi

# Copie o arquivo de exemplo
cp .env.example .env

# Crie estrutura de pastas (se não existir)
mkdir -p services/{animal-service,weighing-service,health-service,nutrition-service,vision-service,market-service}
mkdir -p infra/{postgres,mongodb,redis}
mkdir -p shared
```

### 2. Iniciar Bancos de Dados

```bash
# Com Docker Compose
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs postgres
```

Outputs esperados:
- PostgreSQL: `localhost:5432` (admin:admin123)
- MongoDB: `localhost:27017` (admin:admin123)
- Redis: `localhost:6379`
- MinIO: `localhost:9000` (minioadmin:minioadmin)

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
```

### 5. Rodar Aplicação

```bash
# Animal Service
python services/animal-service/main.py

# Acesse: http://localhost:8001
# Docs: http://localhost:8001/docs
```

---

## 📚 Explicação: TDD (Test-Driven Development)

### O Ciclo TDD

```
┌─────────────┐
│   RED 🔴    │  1. Escrever teste que falha
├─────────────┤
│   GREEN 🟢  │  2. Escrever código mínimo para passar
├─────────────┤
│ REFACTOR 🔵 │  3. Melhorar código mantendo testes passando
└─────────────┘
```

### Exemplo Prático: Animal Repository

#### Fase 1️⃣: RED (Escrever Testes)

```python
# services/animal-service/test_animal_repository.py
def test_create_animal_success(animal_repository, animal_create_dto):
    """Teste falha porque repository.create() não existe ainda"""
    animal = animal_repository.create(animal_create_dto)
    assert animal.id is not None
    assert animal.ear_tag == "001"
```

**Status**: ❌ FALHA (o método não existe)

#### Fase 2️⃣: GREEN (Código Mínimo)

```python
# services/animal-service/repository.py
class AnimalRepository:
    def create(self, animal_data: AnimalCreate) -> AnimalModel:
        animal = AnimalModel(**animal_data.model_dump())
        self.db.add(animal)
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
