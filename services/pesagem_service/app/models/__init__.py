"""
SQLAlchemy Models
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Pesagem(Base):
    """Modelo ORM para Pesagem"""
    __tablename__ = "pesagens"

    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, nullable=False, index=True)
    peso_kg = Column(Float, nullable=False)
    peso_arroba = Column(Float, nullable=True)  # Calculado
    data = Column(Date, nullable=False, index=True)
    hora = Column(String(5), nullable=True)
    observacoes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Pesagem(id={self.id}, animal_id={self.animal_id}, peso_kg={self.peso_kg})>"
