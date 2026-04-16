from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date, timedelta, datetime
from app.models import Cotacao


class CotacaoRepository:
    """Repository para operações de Cotacao"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def criar(self, cotacao_data: dict) -> Cotacao:
        """Cria uma nova cotação"""
        # Garantir que data_referencia é um objeto date
        if isinstance(cotacao_data.get("data_referencia"), str):
            from datetime import datetime as dt
            cotacao_data["data_referencia"] = dt.strptime(
                cotacao_data["data_referencia"], "%Y-%m-%d"
            ).date()
        
        cotacao = Cotacao(**cotacao_data)
        self.db.add(cotacao)
        self.db.commit()
        self.db.refresh(cotacao)
        return cotacao
    
    def obter_por_id(self, cotacao_id: int) -> Cotacao:
        """Obtém uma cotação por ID"""
        return self.db.query(Cotacao).filter(Cotacao.id == cotacao_id).first()
    
    def listar(self, skip: int = 0, limit: int = 100) -> list[Cotacao]:
        """Lista todas as cotações com paginação"""
        return self.db.query(Cotacao).offset(skip).limit(limit).all()
    
    def atualizar(self, cotacao: Cotacao) -> Cotacao:
        """Atualiza uma cotação existente"""
        self.db.commit()
        self.db.refresh(cotacao)
        return cotacao
    
    def deletar(self, cotacao: Cotacao):
        """Deleta uma cotação"""
        self.db.delete(cotacao)
        self.db.commit()
    
    def contar(self) -> int:
        """Conta total de cotações"""
        return self.db.query(Cotacao).count()
    
    def obter_atual(self) -> Cotacao:
        """Obtém a cotação mais recente"""
        return self.db.query(Cotacao).order_by(desc(Cotacao.data_referencia)).first()
    
    def obter_historico(self, dias: int = 30) -> list[Cotacao]:
        """Obtém o histórico de cotações dos últimos N dias"""
        data_inicio = date.today() - timedelta(days=dias)
        return self.db.query(Cotacao).filter(
            Cotacao.data_referencia >= data_inicio
        ).order_by(desc(Cotacao.data_referencia)).all()
    
    def obter_por_date_range(self, data_inicio: date, data_fim: date) -> list[Cotacao]:
        """Obtém cotações entre duas datas"""
        return self.db.query(Cotacao).filter(
            Cotacao.data_referencia >= data_inicio,
            Cotacao.data_referencia <= data_fim
        ).order_by(Cotacao.data_referencia).all()
