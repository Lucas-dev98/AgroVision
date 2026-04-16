"""
API Endpoints para Animal Service
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.services import AnimalService
from app.schemas import AnimalCreate, AnimalUpdate, AnimalResponse, AnimalListResponse
from app.core.database import get_db

router = APIRouter(
    prefix="/api/v1/animals",
    tags=["animals"]
)


@router.post("", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
def criar_animal(animal_data: AnimalCreate, db: Session = Depends(get_db)):
    """
    Cria novo animal
    
    **Exemplo:**
    ```json
    {
      "nome": "Boi Bravo",
      "raca": "Nelore",
      "data_nascimento": "2020-01-15",
      "rfid": "BOI_001"
    }
    ```
    """
    try:
        service = AnimalService(db)
        return service.criar_animal(animal_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=AnimalListResponse)
def listar_animais(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos os animais com paginação
    """
    service = AnimalService(db)
    animais = service.listar_animais(skip, limit)
    total = service.contar_animais()
    return AnimalListResponse(total=total, animais=animais)


@router.get("/{animal_id}", response_model=AnimalResponse)
def obter_animal(animal_id: int, db: Session = Depends(get_db)):
    """
    Obtém detalhes de um animal
    """
    service = AnimalService(db)
    animal = service.obter_animal(animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal


@router.get("/rfid/{rfid}", response_model=AnimalResponse)
def obter_por_rfid(rfid: str, db: Session = Depends(get_db)):
    """
    Obtém animal por RFID
    """
    service = AnimalService(db)
    animal = service.obter_por_rfid(rfid)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal


@router.put("/{animal_id}", response_model=AnimalResponse)
def atualizar_animal(animal_id: int, animal_data: AnimalUpdate, db: Session = Depends(get_db)):
    """
    Atualiza um animal
    """
    service = AnimalService(db)
    animal = service.atualizar_animal(animal_id, animal_data)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_animal(animal_id: int, db: Session = Depends(get_db)):
    """
    Deleta um animal
    """
    service = AnimalService(db)
    if not service.deletar_animal(animal_id):
        raise HTTPException(status_code=404, detail="Animal não encontrado")
