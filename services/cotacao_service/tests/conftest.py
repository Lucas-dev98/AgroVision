import os
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.models import Base


# Configurar DATABASE_URL para usar SQLite em memória para testes
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Cria um engine SQLite em memória para os testes"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Cria uma sessão de banco de dados para testes"""
    from app.core import get_db
    
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    session = TestingSessionLocal()
    
    # Sobrescrever get_db para usar a sessão de teste
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """Cria um cliente de teste do FastAPI"""
    return TestClient(app)


@pytest.fixture(scope="function")
def cotacao_data() -> dict:
    """Dados padrão para criação de cotação nos testes"""
    return {
        "preco_arroba": 250.50,
        "data_referencia": "2026-04-15"
    }
