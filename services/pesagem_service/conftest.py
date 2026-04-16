"""
Configuração Pytest - Fixtures compartilhadas para testes
TDD Phase 2: Setup para testes de Pesagem
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


@pytest.fixture
def pesagem_data():
    """Dados de teste para pesagem"""
    return {
        "peso_kg": 450.5,
        "animal_id": 1,
        "data": "2026-04-15"
    }
