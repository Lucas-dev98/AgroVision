"""
Configuração de banco de dados PostgreSQL (SQLAlchemy)
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

# ==================== CONFIGURAÇÃO ====================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin123@localhost:5432/boi_db"
)

# Pool de conexões
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifica conexão antes de usar
    echo=os.getenv("DEBUG", "False") == "True"
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para ORM models
Base = declarative_base()


# ==================== HELPER FUNCTIONS ====================

def get_db():
    """
    Dependency para FastAPI: retorna sessão do banco
    
    Usage:
        @app.get("/animals")
        def list_animals(db: Session = Depends(get_db)):
            return db.query(Animal).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Cria todas as tabelas"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    CUIDADO: Drop todas as tabelas
    Use apenas para testes e desenvolvimento
    """
    Base.metadata.drop_all(bind=engine)


# ==================== EVENTOS ====================

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Configurações ao conectar (específico para engines diferentes)
    """
    pass
