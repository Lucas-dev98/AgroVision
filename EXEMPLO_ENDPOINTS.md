"""
EXEMPLO: Como Criar Endpoints FastAPI com TDD
Este arquivo é um exemplo/template para próximas implementações

Fluxo:
1. Escrever testes (test_routes.py)
2. Criar routes (routes.py)
3. Integrar em app.py
"""

# ==================== test_routes.py ====================
"""
from fastapi.testclient import TestClient
from app import app
from shared.schemas import AnimalCreate, AnimalStatus

client = TestClient(app)

def test_create_animal_route(db):
    '''Teste do endpoint POST /animals'''
    animal_data = {
        "ear_tag": "001",
        "name": "Bessie",
        "breed": "Nelore",
        "gender": "F"
    }
    response = client.post("/animals", json=animal_data)
    
    assert response.status_code == 201
    assert response.json()["ear_tag"] == "001"
    assert "id" in response.json()

def test_get_animal_route(db):
    '''Teste do endpoint GET /animals/{id}'''
    # Criar animal
    animal_data = {...}
    create_response = client.post("/animals", json=animal_data)
    animal_id = create_response.json()["id"]
    
    # Buscar animal
    response = client.get(f"/animals/{animal_id}")
    
    assert response.status_code == 200
    assert response.json()["id"] == str(animal_id)

def test_list_animals_route(db):
    '''Teste do endpoint GET /animals'''
    response = client.get("/animals")
    
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()
"""

# ==================== routes.py ====================
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.schemas import (
    AnimalCreate, AnimalResponse, AnimalUpdate, 
    AnimalListResponse, AnimalStatus
)
from services.animal_service.repository import AnimalRepository

router = APIRouter(
    prefix="/animals",
    tags=["animals"]
)

@router.post("", response_model=AnimalResponse, status_code=201)
def create_animal(
    animal: AnimalCreate,
    db: Session = Depends(get_db)
):
    '''Criar novo animal'''
    repo = AnimalRepository(db)
    return repo.create(animal)

@router.get("/{animal_id}", response_model=AnimalResponse)
def get_animal(
    animal_id: str,
    db: Session = Depends(get_db)
):
    '''Obter animal por ID'''
    from uuid import UUID
    repo = AnimalRepository(db)
    animal = repo.get_by_id(UUID(animal_id))
    
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animal não encontrado"
        )
    return animal

@router.get("", response_model=AnimalListResponse)
def list_animals(
    skip: int = 0,
    limit: int = 100,
    status_filter: AnimalStatus = None,
    db: Session = Depends(get_db)
):
    '''Listar animais'''
    repo = AnimalRepository(db)
    animals, total = repo.list_all(
        skip=skip,
        limit=limit,
        status=status_filter
    )
    
    return {
        "total": total,
        "items": animals,
        "page": skip // limit + 1 if total > 0 else 1,
        "page_size": limit
    }

@router.put("/{animal_id}", response_model=AnimalResponse)
def update_animal(
    animal_id: str,
    update: AnimalUpdate,
    db: Session = Depends(get_db)
):
    '''Atualizar animal'''
    from uuid import UUID
    repo = AnimalRepository(db)
    animal = repo.update(UUID(animal_id), update)
    
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animal não encontrado"
        )
    return animal

@router.delete("/{animal_id}", status_code=204)
def delete_animal(
    animal_id: str,
    db: Session = Depends(get_db)
):
    '''Deletar animal (soft delete)'''
    from uuid import UUID
    repo = AnimalRepository(db)
    success = repo.delete(UUID(animal_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animal não encontrado"
        )
"""

# ==================== app.py (integração) ====================
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from shared.database import init_db
from routes import router  # Importar router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Animal Service...")
    init_db()
    yield
    # Shutdown
    print("🛑 Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)  # Incluir router

@app.get("/health")
def health():
    return {"status": "alive"}
"""

# ==================== main.py ====================
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
"""

# ==================== COMO EXECUTAR ====================
"""
1. Criar arquivo routes.py com os endpoints (TDD - escrever testes primeiro)
2. Criar arquivo test_routes.py com os testes
3. Executar: make test
4. Quando testes passam, integrar routes em app.py
5. Ejecutar: make run
6. Acessar: http://localhost:8001/docs

Exemplo de Teste:
  POST /animals
  Input: {"ear_tag": "001", "breed": "Nelore", "gender": "F"}
  Output: {"id": "uuid", "ear_tag": "001", ..., "created_at": "2026-04-15T..."}

  GET /animals
  Output: {"total": 1, "items": [...], "page": 1, "page_size": 100}

  GET /animals/{id}
  Output: {"id": "uuid", "ear_tag": "001", ...}

  PUT /animals/{id}
  Input: {"status": "sold"}
  Output: {..., "status": "sold"}

  DELETE /animals/{id}
  Output: 204 (sem body)
"""
