"""
API Endpoints para Pesagem Service
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date
from sqlalchemy.orm import Session

from app.services import PesagemService
from app.schemas import PesagemCreate, PesagemUpdate, PesagemResponse, GanhoResponse
from app.core.database import get_db

router = APIRouter(
    prefix="/api/v1/pesagens",
    tags=["pesagens"]
)


@router.post("", response_model=PesagemResponse, status_code=status.HTTP_201_CREATED)
def registrar_pesagem(pesagem_data: PesagemCreate, db: Session = Depends(get_db)):
    """
    Registra nova pesagem
    
    Exemplo:
    ```json
    {
      "animal_id": 1,
      "peso_kg": 450.5,
      "data": "2026-04-15"
    }
    ```
    """
    service = PesagemService(db)
    return service.registrar_pesagem(pesagem_data)


@router.get("/{pesagem_id}", response_model=PesagemResponse)
def obter_pesagem(pesagem_id: int, db: Session = Depends(get_db)):
    """Obtém pesagem por ID"""
    service = PesagemService(db)
    pesagem = service.obter_pesagem(pesagem_id)
    if not pesagem:
        raise HTTPException(status_code=404, detail="Pesagem não encontrada")
    return pesagem


@router.get("/animal/{animal_id}/historico")
def obter_historico(animal_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtém histórico de pesagens de um animal"""
    service = PesagemService(db)
    pesagens = service.obter_historico(animal_id, skip, limit)
    total = service.contar_pesagens_animal(animal_id)
    return {"total": total, "pesagens": pesagens}


@router.get("/animal/{animal_id}/ultima")
def obter_ultima(animal_id: int, db: Session = Depends(get_db)):
    """Obtém última pesagem de um animal"""
    service = PesagemService(db)
    pesagem = service.obter_ultima_pesagem(animal_id)
    if not pesagem:
        raise HTTPException(status_code=404, detail="Nenhuma pesagem encontrada")
    return pesagem


@router.get("/animal/{animal_id}/ganho")
def obter_ganho(animal_id: int, data_inicio: date, data_fim: date, db: Session = Depends(get_db)):
    """Calcula ganho de peso entre duas datas"""
    service = PesagemService(db)
    ganho = service.calcular_ganho(animal_id, data_inicio, data_fim)
    if not ganho:
        raise HTTPException(status_code=404, detail="Dados insuficientes para cálculo")
    return ganho


@router.put("/{pesagem_id}", response_model=PesagemResponse)
def atualizar_pesagem(pesagem_id: int, pesagem_data: PesagemUpdate, db: Session = Depends(get_db)):
    """Atualiza pesagem"""
    service = PesagemService(db)
    pesagem = service.atualizar_pesagem(pesagem_id, pesagem_data)
    if not pesagem:
        raise HTTPException(status_code=404, detail="Pesagem não encontrada")
    return pesagem


@router.delete("/{pesagem_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pesagem(pesagem_id: int, db: Session = Depends(get_db)):
    """Deleta pesagem"""
    service = PesagemService(db)
    if not service.deletar_pesagem(pesagem_id):
        raise HTTPException(status_code=404, detail="Pesagem não encontrada")
