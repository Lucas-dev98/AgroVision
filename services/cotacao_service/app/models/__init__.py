from sqlalchemy import Column, Integer, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, datetime

Base = declarative_base()


class Cotacao(Base):
    """Model ORM para Cotação"""
    __tablename__ = "cotacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    preco_arroba = Column(Float, nullable=False, index=True)
    data_referencia = Column(Date, nullable=False, index=True)
    criada_em = Column(DateTime, default=datetime.now)
    atualizada_em = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Cotacao(id={self.id}, preco_arroba={self.preco_arroba}, data_referencia={self.data_referencia})>"
