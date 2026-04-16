# 🧪 Metodologia TDD (Test-Driven Development)

## Fluxo TDD

```
1. Red   → Escrever teste que falha
2. Green → Implementar código mínimo que passa
3. Refactor → Melhorar sem quebrar testes
```

## Estrutura de Testes por Serviço

```
service-name/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── animal.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── animal.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── animal_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── animal_repository.py
│   └── core/
│       ├── __init__.py
│       └── config.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_schemas.py
│   ├── test_services.py
│   ├── test_repositories.py
│   └── test_endpoints.py
├── Dockerfile
├── requirements.txt
└── pytest.ini
```

## Exemplo Completo: animal-service

### 1️⃣ Teste da Model

```python
# tests/test_models.py
from datetime import date
from app.models.animal import Animal

def test_animal_creation():
    animal = Animal(
        nome="Boi Bravo",
        raca="Nelore",
        data_nascimento=date(2020, 1, 15),
        rfid="BOI_001"
    )
    assert animal.nome == "Boi Bravo"
    assert animal.status == "ativo"
    assert animal.rfid == "BOI_001"
```

### 2️⃣ Teste do Repository

```python
# tests/test_repositories.py
import pytest
from app.repositories.animal_repository import AnimalRepository
from app.models.animal import Animal
from datetime import date

@pytest.fixture
def repo(db_session):
    return AnimalRepository(db_session)

def test_create_animal(repo):
    animal_data = {
        "nome": "Boi Bravo",
        "raca": "Nelore",
        "data_nascimento": date(2020, 1, 15),
        "rfid": "BOI_001"
    }
    animal = repo.create(animal_data)
    assert animal.id is not None
    assert animal.nome == "Boi Bravo"

def test_get_animal_by_id(repo):
    animal = repo.get_by_id(1)
    assert animal is not None

def test_list_animals(repo):
    animals = repo.list_all()
    assert len(animals) >= 0
```

### 3️⃣ Teste do Schema

```python
# tests/test_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas.animal import AnimalCreate, AnimalResponse
from datetime import date

def test_animal_create_valid():
    data = {
        "nome": "Boi Bravo",
        "raca": "Nelore",
        "data_nascimento": date(2020, 1, 15),
        "rfid": "BOI_001"
    }
    schema = AnimalCreate(**data)
    assert schema.nome == "Boi Bravo"

def test_animal_create_invalid_rfid():
    data = {
        "nome": "Boi Bravo",
        "rfid": ""  # Inválido: vazio
    }
    with pytest.raises(ValidationError):
        AnimalCreate(**data)
```

### 4️⃣ Teste do Service

```python
# tests/test_services.py
import pytest
from app.services.animal_service import AnimalService
from datetime import date

@pytest.fixture
def service(mock_repo):
    return AnimalService(mock_repo)

def test_create_animal(service):
    animal_data = {
        "nome": "Boi Bravo",
        "raca": "Nelore",
        "data_nascimento": date(2020, 1, 15),
        "rfid": "BOI_001"
    }
    animal = service.create(animal_data)
    assert animal.id is not None

def test_get_animal(service):
    animal = service.get_by_id(1)
    assert animal.nome == "Boi Bravo"
```

### 5️⃣ Teste dos Endpoints

```python
# tests/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import date

@pytest.fixture
def client():
    return TestClient(app)

def test_create_animal_endpoint(client):
    response = client.post(
        "/animals",
        json={
            "nome": "Boi Bravo",
            "raca": "Nelore",
            "data_nascimento": "2020-01-15",
            "rfid": "BOI_001"
        }
    )
    assert response.status_code == 201
    assert response.json()["nome"] == "Boi Bravo"

def test_list_animals_endpoint(client):
    response = client.get("/animals")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_animal_endpoint(client):
    response = client.get("/animals/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
```

## Fixtures Comuns (conftest.py)

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import Base

@pytest.fixture(scope="session")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(test_db):
    connection = test_db.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    from fastapi.testclient import TestClient
    from app.main import app
    
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## Executando Testes

### Todos os testes
```bash
pytest
```

### Com coverage
```bash
pytest --cov=app --cov-report=html
```

### Testes específicos
```bash
pytest tests/test_services.py::test_create_animal -v
```

### Watch mode (pytest-watch)
```bash
ptw
```

## Cobertura Esperada

- **Models**: 100%
- **Schemas**: 100%
- **Services**: 90%+
- **Repositories**: 90%+
- **Endpoints**: 85%+

## 🎯 Objetivos de Qualidade

✅ Mínimo 80% de cobertura geral
✅ Todos os casos de sucesso cobertos
✅ Todos os erros cobertos
✅ Testes rápidos (<1s por teste)
✅ Dados de teste isolados (fixtures)
