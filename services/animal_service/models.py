"""
Modelos SQLAlchemy para Animal Service
"""
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Text, Numeric
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from shared.database import Base
from shared.schemas import AnimalStatus, AnimalGender


# Tipo UUID compatível com SQLite e PostgreSQL
def get_uuid_column():
    """Retorna coluna UUID compatível com ambos os bancos"""
    import os
    # Em testes (SQLite), usar String; em produção (PostgreSQL), usar PG_UUID
    if os.getenv("DATABASE_URL", "").startswith("postgresql"):
        return PG_UUID(as_uuid=True)
    else:
        # SQLite em testes
        return String(36)


class AnimalModel(Base):
    """Modelo ORM para Animal"""
    __tablename__ = "animals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ear_tag = Column(String(20), unique=True, nullable=True, index=True)
    name = Column(String(100), nullable=True)
    breed = Column(String(50), nullable=False, index=True)
    birth_date = Column(DateTime, nullable=True)
    gender = Column(SQLEnum(AnimalGender), nullable=False)
    status = Column(SQLEnum(AnimalStatus), nullable=False, default=AnimalStatus.ACTIVE, index=True)
    
    # Relacionamentos de filiação
    mother_id = Column(String(36), ForeignKey("animals.id"), nullable=True)
    father_id = Column(String(36), ForeignKey("animals.id"), nullable=True)
    
    detected_by_yolo = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Audit fields (sem FK para não complicar testes)
    # created_by será adicionado em produção com User model
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relacionamentos
    weighing_records = relationship("WeighingRecordModel", back_populates="animal", cascade="all, delete-orphan")
    vaccines = relationship("VaccineModel", back_populates="animal", cascade="all, delete-orphan")
    feeding_records = relationship("FeedingRecordModel", back_populates="animal", cascade="all, delete-orphan")


class WeighingRecordModel(Base):
    """Modelo ORM para Weighing Record"""
    __tablename__ = "weighing_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    animal_id = Column(String(36), ForeignKey("animals.id"), nullable=False, index=True)
    weight_kg = Column(Numeric(8, 2), nullable=False)
    weight_arrobas = Column(Numeric(8, 2), nullable=False)
    recorded_at = Column(DateTime, nullable=False, index=True)
    # recorded_by será adicionado em produção
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relacionamentos
    animal = relationship("AnimalModel", back_populates="weighing_records")


class VaccineModel(Base):
    """Modelo ORM para Vaccine"""
    __tablename__ = "vaccines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    animal_id = Column(String(36), ForeignKey("animals.id"), nullable=False, index=True)
    vaccine_name = Column(String(100), nullable=False)
    application_date = Column(DateTime, nullable=False)
    next_dose_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum('applied', 'pending', 'overdue', name='vaccine_status'), nullable=False)
    veterinarian = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # created_by será adicionado em produção
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relacionamentos
    animal = relationship("AnimalModel", back_populates="vaccines")


class FeedingRecordModel(Base):
    """Modelo ORM para Feeding Record"""
    __tablename__ = "feeding_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    animal_id = Column(String(36), ForeignKey("animals.id"), nullable=False, index=True)
    feed_type = Column(String(100), nullable=False)
    quantity_kg = Column(Numeric(8, 2), nullable=False)
    fed_at = Column(DateTime, nullable=False)
    # recorded_by será adicionado em produção
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relacionamentos
    animal = relationship("AnimalModel", back_populates="feeding_records")
