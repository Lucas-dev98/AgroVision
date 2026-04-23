"""
Configurações de testes e fixtures
"""
import pytest
import os
import sys
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Create a temporary database file for tests
test_db_fd, test_db_path = tempfile.mkstemp()
DATABASE_URL = f"sqlite:///{test_db_path}"

# Set environment variable
os.environ["DATABASE_URL"] = DATABASE_URL

@pytest.fixture(scope="session", autouse=True)
def cleanup_db():
    """Clean up database after all tests"""
    yield
    # Cleanup file after all tests
    try:
        os.close(test_db_fd)
        os.unlink(test_db_path)
    except:
        pass


@pytest.fixture(scope="session")
def test_engine():
    """Cria engine de teste"""
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Import e criar tabelas
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def reset_db(test_engine):
    """Reset database before each test"""
    from app.models import Base
    
    # Clear all tables
    with test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    
    yield


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
def client(test_engine):
    """Cria cliente TestClient"""
    # Import app AFTER database URL is set
    from app.main import app
    from shared.database import get_db
    from app.models import Base
    
    # Ensure tables exist
    Base.metadata.create_all(bind=test_engine)
    
    def override_get_db():
        connection = test_engine.connect()
        transaction = connection.begin()
        db = sessionmaker(bind=connection)()
        try:
            yield db
        finally:
            db.close()
            transaction.rollback()
            connection.close()
    
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
