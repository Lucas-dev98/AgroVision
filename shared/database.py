"""Configuração compartilhada de banco de dados para todos os serviços"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Determinar DATABASE_URL
# Para produção: postgresql://user:password@host:port/database
# Para testes/desenvolvimento: sqlite:///./agrovision.db ou sqlite:///:memory:
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv("DATABASE_URL_DEV", "sqlite:///./agrovision.db")
)

# Determinar argumentos de conexão baseado no tipo de banco
if "postgresql" in DATABASE_URL:
    connect_args = {}
    pool_pre_ping = True
else:
    # SQLite para testes/desenvolvimento
    connect_args = {"check_same_thread": False}
    pool_pre_ping = False

# Criar engine com configurações apropriadas
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=pool_pre_ping,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"
)

# Criar SessionLocal factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator:
    """Dependency injection para SQLAlchemy session - pode ser usado em todos os serviços"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar banco de dados com as tabelas (usar Base.metadata de cada serviço)"""
    # Esta função deve ser chamada com o Base correto de cada serviço
    pass
