"""
SQLAlchemy Models
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
from enum import Enum as PythonEnum

from app.schemas import AnimalStatus

Base = declarative_base()


class Animal(Base):
    """Modelo ORM para Animal"""
    __tablename__ = "animais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    raca = Column(String(50), nullable=False, index=True)
    data_nascimento = Column(Date, nullable=True)
    rfid = Column(String(50), unique=True, nullable=True, index=True)
    lote_id = Column(Integer, nullable=True)
    status = Column(Enum(AnimalStatus), default=AnimalStatus.ATIVO, nullable=False, server_default=AnimalStatus.ATIVO)
    peso_inicial = Column(Integer, nullable=True)
    data_entrada = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, **kwargs):
        """Inicializa Animal com status padrão"""
        if 'status' not in kwargs:
            kwargs['status'] = AnimalStatus.ATIVO
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Animal(id={self.id}, nome={self.nome}, raca={self.raca})>"
