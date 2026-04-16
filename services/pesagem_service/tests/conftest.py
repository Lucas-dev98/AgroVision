"""
Configurações de testes e fixtures
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import date

# Force SQLite para testes
DATABASE_URL = "sqlite:///:memory:"

# Definir variável de ambiente para app usar SQLite
os.environ["DATABASE_URL"] = DATABASE_URL


@pytest.fixture(scope="session")
def test_engine():
    """Cria engine de teste"""
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine) -> Session:
    """Cria sessão de banco para teste"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Cria cliente TestClient"""
    from app.main import app
    from shared.database import get_db
    
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()


@pytest.fixture
def pesagem_data():
    """Dados de teste para pesagem"""
    return {
        "animal_id": 1,
        "peso_kg": 450.0,
        "data": date(2026, 4, 15)
    }
