"""Database configuration for Pesagem Service"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Base

# Criar engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar todas as tabelas
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency injection para SQLAlchemy session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
