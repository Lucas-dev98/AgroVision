"""
Configurações de testes e fixtures
"""
import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Force SQLite para testes
DATABASE_URL = "sqlite:///:memory:"

# Definir variável de ambiente para app usar SQLite em testes
os.environ["DATABASE_URL"] = DATABASE_URL

@pytest.fixture(scope="session")
def test_engine():
    """Cria engine de teste"""
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
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
def animal_data():
    """Dados de teste para animal"""
    from datetime import date
    return {
        "nome": "Boi Bravo",
        "raca": "Nelore",
        "data_nascimento": date(2020, 1, 15),
        "rfid": "BOI_001"
    }
