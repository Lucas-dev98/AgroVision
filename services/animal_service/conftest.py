"""
Configuração Pytest - Fixtures compartilhadas para testes
TDD Phase 1: Setup para testes
"""
import pytest
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Adicionar diretório raiz ao PYTHONPATH para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Usar banco SQLite em memória para testes (rápido e isolado)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Cria engine SQLite em memória para toda sessão de testes"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Desabilitar enforcement de FK no SQLite (só pros testes)
    def disable_fk_enforcement(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()
    
    from sqlalchemy import event
    event.listen(engine, "connect", disable_fk_enforcement)
    
    # Importar Base e criar tabelas
    from app.models import Base
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(engine) -> Session:
    """Cria sessão do banco para cada teste (transação isolada)"""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    # Rollback após o teste (garante isolamento)
    session.close()
    transaction.rollback()
    connection.close()


# ==================== FIXTURES DE DADOS ====================

@pytest.fixture
def valid_animal_data():
    """Dados válidos para criar um animal"""
    return {
        "ear_tag": "001",
        "name": "Bessie",
        "breed": "Nelore",
        "birth_date": datetime.now() - timedelta(days=730),  # 2 anos
        "gender": "F",
        "status": "active",
        "detected_by_yolo": False,
        "notes": "Animal de teste"
    }


@pytest.fixture
def valid_animal_data_2():
    """Segundo animal válido para testes"""
    return {
        "ear_tag": "002",
        "name": "Ferdinand",
        "breed": "Brahman",
        "birth_date": datetime.now() - timedelta(days=1095),  # 3 anos
        "gender": "M",
        "status": "active",
        "detected_by_yolo": True,
        "notes": "Animal detectado por YOLO"
    }


@pytest.fixture
def invalid_animal_data():
    """Dados inválidos (faltam campos obrigatórios)"""
    return {
        "ear_tag": "003",
        # Falta: breed, gender
    }


@pytest.fixture
def animal_create_dto(valid_animal_data):
    """DTO para criar animal"""
    from shared.schemas import AnimalCreate
    return AnimalCreate(**valid_animal_data)


@pytest.fixture
def animal_create_dto_2(valid_animal_data_2):
    """Segundo DTO para criar animal"""
    from shared.schemas import AnimalCreate
    return AnimalCreate(**valid_animal_data_2)


# ==================== FIXTURES PARA REPOSITÓRIO ====================

@pytest.fixture
def animal_repository(db):
    """Instancia repositório com banco de teste"""
    # Usar importação relativa
    import sys
    from pathlib import Path
    root_path = Path(__file__).parent.parent.parent
    if str(root_path) not in sys.path:
        sys.path.insert(0, str(root_path))
    
    from services.animal_service.repository import AnimalRepository
    return AnimalRepository(db=db)


@pytest.fixture
def created_animal(animal_repository, animal_create_dto):
    """Cria um animal no banco para testes que precisam de animal existente"""
    return animal_repository.create(animal_create_dto)


@pytest.fixture
def created_animal_2(animal_repository, animal_create_dto_2):
    """Cria segundo animal no banco"""
    return animal_repository.create(animal_create_dto_2)


# ==================== FIXTURES PARA API ====================

@pytest.fixture
def client(db):
    """Cliente FastAPI para testes"""
    from fastapi.testclient import TestClient
    from app import app
    
    # Override dependency para usar DB de testes
    from app.core.database import get_db
    
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    # Limpar overrides
    app.dependency_overrides.clear()
