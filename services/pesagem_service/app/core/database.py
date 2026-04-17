"""Database configuration for Pesagem Service"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings
from app.models import Base

# Configurar engine com retry e pool
pool_class = NullPool if "sqlite" in settings.DATABASE_URL else QueuePool
connect_args = {}

if "sqlite" not in settings.DATABASE_URL:
    connect_args = {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
    }

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=pool_class,
    connect_args=connect_args,
    pool_pre_ping=True,  # Validar conexão antes de usar
    echo=False,
)

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# NOTA: Base.metadata.create_all() foi removido.
# Use Alembic migrations ou execute manualmente conforme necessário.


def get_db():
    """Dependency injection para SQLAlchemy session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
