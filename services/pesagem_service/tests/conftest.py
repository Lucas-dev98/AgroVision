"""
Configurações de testes e fixtures
"""
import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import date

# Create a temporary database file for tests
test_db_fd, test_db_path = tempfile.mkstemp()
DATABASE_URL = f"sqlite:///{test_db_path}"

# Definir variável de ambiente para app usar SQLite
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
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


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
def pesagem_data():
    """Dados de teste para pesagem"""
    return {
        "animal_id": 1,
        "peso_kg": 450.0,
        "data": date(2026, 4, 15)
    }
