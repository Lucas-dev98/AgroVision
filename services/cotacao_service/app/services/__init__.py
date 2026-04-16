from sqlalchemy.orm import Session
from datetime import date
from app.models import Cotacao
from app.repositories import CotacaoRepository
from app.schemas import CotacaoCreate, CotacaoUpdate


class CotacaoService:
    """Service contém a lógica de negócio para cotações"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = CotacaoRepository(db) if db else None
    
    def criar_cotacao(self, cotacao_data: dict) -> Cotacao:
        """Cria uma nova cotação com validações"""
        if cotacao_data.get("preco_arroba", 0) <= 0:
            raise ValueError("Preço deve ser maior que zero")
        
        return self.repo.criar(cotacao_data)
    
    def obter_cotacao_por_id(self, cotacao_id: int) -> Cotacao:
        """Obtém uma cotação por ID"""
        return self.repo.obter_por_id(cotacao_id)
    
    def listar_cotacoes(self, skip: int = 0, limit: int = 100) -> list[Cotacao]:
        """Lista todas as cotações"""
        return self.repo.listar(skip=skip, limit=limit)
    
    def obter_cotacao_atual(self) -> Cotacao:
        """Obtém a cotação mais recente"""
        return self.repo.obter_atual()
    
    def obter_historico_periodo(self, data_inicio: date, data_fim: date) -> list[Cotacao]:
        """Obtém histórico de cotações em um período"""
        return self.repo.obter_por_date_range(data_inicio, data_fim)
    
    def obter_media_preco(self, dias: int = 30) -> float:
        """Calcula a média de preço dos últimos N dias"""
        cotacoes = self.repo.obter_historico(dias=dias)
        if not cotacoes:
            return 0.0
        
        total = sum(c.preco_arroba for c in cotacoes)
        return total / len(cotacoes)
    
    @staticmethod
    def calcular_valor_total(peso_arroba: float, preco_arroba: float) -> float:
        """Calcula o valor total (peso em arroba * preço)"""
        return peso_arroba * preco_arroba
    
    def atualizar_cotacao(self, cotacao_id: int, dados_atualizacao: dict) -> Cotacao:
        """Atualiza uma cotação existente"""
        cotacao = self.repo.obter_por_id(cotacao_id)
        if not cotacao:
            return None
        
        if "preco_arroba" in dados_atualizacao:
            if dados_atualizacao["preco_arroba"] <= 0:
                raise ValueError("Preço deve ser maior que zero")
            cotacao.preco_arroba = dados_atualizacao["preco_arroba"]
        
        if "data_referencia" in dados_atualizacao:
            cotacao.data_referencia = dados_atualizacao["data_referencia"]
        
        return self.repo.atualizar(cotacao)
    
    def deletar_cotacao(self, cotacao_id: int):
        """Deleta uma cotação"""
        cotacao = self.repo.obter_por_id(cotacao_id)
        if cotacao:
            self.repo.deletar(cotacao)
