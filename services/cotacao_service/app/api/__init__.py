from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from app.core import get_db
from app.services import CotacaoService
from app.schemas import (
    CotacaoCreate,
    CotacaoUpdate,
    CotacaoResponse,
    MediaResponse
)

router = APIRouter(prefix="/api/v1/cotacoes", tags=["cotacoes"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CotacaoResponse)
def criar_cotacao(cotacao: CotacaoCreate, db: Session = Depends(get_db)):
    """Criar uma nova cotação"""
    service = CotacaoService(db)
    try:
        nova_cotacao = service.criar_cotacao(cotacao.model_dump())
        return nova_cotacao
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/atual", response_model=CotacaoResponse)
def obter_cotacao_atual(db: Session = Depends(get_db)):
    """Obter a cotação mais recente"""
    service = CotacaoService(db)
    cotacao = service.obter_cotacao_atual()
    
    if not cotacao:
        raise HTTPException(status_code=404, detail="Nenhuma cotação encontrada")
    
    return cotacao


@router.get("/historico", response_model=list[CotacaoResponse])
def obter_historico(
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obter histórico das últimas N cotações"""
    service = CotacaoService(db)
    repo = service.repo
    cotacoes = repo.obter_historico(dias=dias)
    
    if not cotacoes:
        raise HTTPException(status_code=404, detail="Nenhuma cotação encontrada")
    
    return cotacoes


@router.get("/media", response_model=MediaResponse)
def obter_media_preco(
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obter média de preço dos últimos N dias"""
    service = CotacaoService(db)
    
    from datetime import timedelta
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=dias)
    
    media = service.obter_media_preco(dias=dias)
    
    return MediaResponse(
        media=media,
        dias=dias,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@router.get("/{cotacao_id}", response_model=CotacaoResponse)
def obter_cotacao(cotacao_id: int, db: Session = Depends(get_db)):
    """Obter uma cotação por ID"""
    service = CotacaoService(db)
    cotacao = service.obter_cotacao_por_id(cotacao_id)
    
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    return cotacao


@router.get("", response_model=list[CotacaoResponse])
def listar_cotacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar todas as cotações"""
    service = CotacaoService(db)
    return service.listar_cotacoes(skip=skip, limit=limit)


@router.put("/{cotacao_id}", response_model=CotacaoResponse)
def atualizar_cotacao(
    cotacao_id: int,
    cotacao_update: CotacaoUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar uma cotação existente"""
    service = CotacaoService(db)
    
    cotacao_existente = service.obter_cotacao_por_id(cotacao_id)
    if not cotacao_existente:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    try:
        cotacao_atualizada = service.atualizar_cotacao(
            cotacao_id,
            cotacao_update.model_dump(exclude_unset=True)
        )
        return cotacao_atualizada
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cotacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cotacao(cotacao_id: int, db: Session = Depends(get_db)):
    """Deletar uma cotação"""
    service = CotacaoService(db)
    
    cotacao = service.obter_cotacao_por_id(cotacao_id)
    if not cotacao:
        raise HTTPException(status_code=404, detail="Cotação não encontrada")
    
    service.deletar_cotacao(cotacao_id)
