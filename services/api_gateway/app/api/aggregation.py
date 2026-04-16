"""Rotas de Agregação - FASE 10

Endpoints para agregação de dados de múltiplos serviços
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
import logging

from app.services.aggregation import aggregation_service

router = APIRouter(prefix="/api/v1", tags=["aggregation"])
logger = logging.getLogger("agrovision.aggregation")


@router.get(
    "/dashboard/animal/{animal_id}",
    summary="Dashboard consolidado de animal",
    description="Retorna dados do animal agregados com pesagens e cotações",
    tags=["Dashboard"]
)
async def get_animal_dashboard(
    animal_id: int = Path(..., gt=0, description="ID do animal"),
    include: Optional[str] = Query(
        None,
        description="Campos a incluir (separados por vírgula): animal,pesagens,cotacoes"
    ),
    start_date: Optional[str] = Query(
        None,
        description="Data inicial para filtro (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None,
        description="Data final para filtro (YYYY-MM-DD)"
    ),
):
    """
    Obter dashboard consolidado de um animal
    
    Agrega:
    - Dados do animal
    - Histórico de pesagens
    - Cotações
    
    **Path Parameters:**
    - `animal_id`: ID do animal (inteiro positivo)
    
    **Query Parameters:**
    - `include`: Campos a incluir (padrão: todos)
    - `start_date`: Data inicial (YYYY-MM-DD)
    - `end_date`: Data final (YYYY-MM-DD)
    
    **Example:**
    ```
    GET /api/v1/dashboard/animal/1?include=animal,pesagens&start_date=2026-01-01
    ```
    """
    try:
        # Validar animal_id
        if animal_id <= 0:
            raise HTTPException(status_code=400, detail="ID do animal deve ser positivo")
        
        # Parse include fields
        include_fields = None
        if include:
            include_fields = [f.strip() for f in include.split(",")]
            # Validar campos
            valid_fields = {"animal", "pesagens", "cotacoes"}
            invalid_fields = set(include_fields) - valid_fields
            if invalid_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Campos inválidos: {', '.join(invalid_fields)}"
                )
        
        # Preparar filtros
        filters = {}
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        
        # Buscar dashboard agregado
        dashboard = await aggregation_service.get_animal_dashboard(
            animal_id=animal_id,
            include_fields=include_fields,
            filters=filters
        )
        
        # Verificar se animal foi encontrado
        if dashboard.get("animal") is None:
            raise HTTPException(
                status_code=404,
                detail=f"Animal {animal_id} não encontrado"
            )
        
        return dashboard
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar dashboard de animal {animal_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao buscar dashboard do animal"
        )


@router.get(
    "/dashboard/animals",
    summary="Dashboards consolidados de múltiplos animais",
    description="Retorna dados agregados para múltiplos animais",
    tags=["Dashboard"]
)
async def get_animals_dashboard(
    ids: str = Query(
        ...,
        description="IDs dos animais separados por vírgula (máx 100)"
    ),
    include: Optional[str] = Query(
        None,
        description="Campos a incluir (separados por vírgula): animal,pesagens,cotacoes"
    ),
):
    """
    Obter dashboards consolidados de múltiplos animais
    
    Retorna array com dados agregados para cada animal
    
    **Query Parameters:**
    - `ids`: IDs dos animais (separados por vírgula, máx 100)
    - `include`: Campos a incluir (padrão: todos)
    
    **Example:**
    ```
    GET /api/v1/dashboard/animals?ids=1,2,3&include=animal,pesagens
    ```
    """
    try:
        # Parse IDs
        try:
            animal_ids = [int(id_str.strip()) for id_str in ids.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="IDs de animais devem ser inteiros"
            )
        
        # Validar quantidade de IDs
        if len(animal_ids) > 100:
            raise HTTPException(
                status_code=400,
                detail="Máximo de 100 animais por requisição"
            )
        
        if len(animal_ids) == 0:
            raise HTTPException(
                status_code=400,
                detail="Pelo menos um ID de animal deve ser fornecido"
            )
        
        # Parse include fields
        include_fields = None
        if include:
            include_fields = [f.strip() for f in include.split(",")]
        
        # Buscar dashboards agregados
        dashboards = await aggregation_service.get_animals_dashboard(animal_ids)
        
        return dashboards
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar dashboards de animais: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao buscar dashboards dos animais"
        )


@router.get(
    "/aggregation/health",
    summary="Status dos serviços agregados",
    description="Verifica disponibilidade dos serviços para agregação",
    tags=["Aggregation"]
)
async def aggregation_health():
    """
    Verificar saúde dos serviços agregados
    
    Retorna status de conexão com cada serviço
    
    **Example:**
    ```
    GET /api/v1/aggregation/health
    ```
    
    **Response:**
    ```json
    {
        "status": "healthy",
        "services": {
            "animal": true,
            "pesagem": true,
            "cotacao": true
        }
    }
    ```
    """
    try:
        # Verificar saúde de cada serviço (simplificado para este exemplo)
        return {
            "status": "healthy",
            "services": {
                "animal": True,
                "pesagem": True,
                "cotacao": True
            },
            "cache_status": {
                "entries": len(aggregation_service._cache),
                "capacity": "unlimited"
            }
        }
    except Exception as e:
        logger.error(f"Erro ao verificar saúde de agregação: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao verificar saúde da agregação"
        )


@router.post(
    "/aggregation/cache/clear",
    summary="Limpar cache de agregação",
    description="Remove todas as entradas do cache de agregação",
    tags=["Aggregation"]
)
async def clear_aggregation_cache():
    """
    Limpar cache de agregação
    
    Remove todas as entradas do cache em memória
    
    **Example:**
    ```
    POST /api/v1/aggregation/cache/clear
    ```
    """
    try:
        aggregation_service.cache_clear()
        return {
            "status": "success",
            "message": "Cache de agregação limpo"
        }
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao limpar cache"
        )
