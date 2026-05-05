"""API Gateway - Rotas de Proxy Reverso"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict, Union
from app.services import ProxyService

router = APIRouter()


# ==================== ANIMAL SERVICE ROUTES ====================

@router.api_route("/api/v1/animais", methods=["GET", "POST", "PUT", "DELETE"], response_model=None)
async def proxy_animals_root(request: Request) -> JSONResponse:
    """Roteia requisições para animal-service (root path)"""
    method = request.method
    body = None
    
    if method in ["POST", "PUT"]:
        try:
            body = await request.json()
        except Exception:
            body = None
    
    headers = dict(request.headers)
    
    result = await ProxyService.forward_request(
        path="/api/v1/animals",
        method=method,
        body=body,
        headers=headers,
        service="animal"
    )
    
    if result["status_code"] == 200:
        return result["content"]
    
    raise HTTPException(
        status_code=result["status_code"],
        detail=result["content"]
    )


@router.api_route("/api/v1/animais/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], response_model=None)
async def proxy_animals(path: str, request: Request) -> JSONResponse:
    """Roteia requisições para animal-service"""
    method = request.method
    body = None
    
    if method in ["POST", "PUT"]:
        try:
            body = await request.json()
        except Exception:
            body = None
    
    headers = dict(request.headers)
    
    result = await ProxyService.forward_request(
        path=f"/api/v1/animals/{path}",
        method=method,
        body=body,
        headers=headers,
        service="animal"
    )
    
    if result["status_code"] == 200:
        return result["content"]
    
    raise HTTPException(
        status_code=result["status_code"],
        detail=result["content"]
    )


# ==================== PESAGEM SERVICE ROUTES ====================

@router.api_route("/api/v1/pesagens", methods=["GET", "POST", "PUT", "DELETE"], response_model=None)
async def proxy_pesagens_root(request: Request) -> JSONResponse:
    """Roteia requisições para pesagem-service (root path)"""
    method = request.method
    body = None
    
    if method in ["POST", "PUT"]:
        try:
            body = await request.json()
        except Exception:
            body = None
    
    headers = dict(request.headers)
    
    result = await ProxyService.forward_request(
        path="/api/v1/pesagens",
        method=method,
        body=body,
        headers=headers,
        service="pesagem"
    )
    
    if result["status_code"] == 200:
        return result["content"]
    
    raise HTTPException(
        status_code=result["status_code"],
        detail=result["content"]
    )


@router.api_route("/api/v1/pesagens/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], response_model=None)
async def proxy_pesagens(path: str, request: Request) -> JSONResponse:
    """Roteia requisições para pesagem-service"""
    method = request.method
    body = None
    
    if method in ["POST", "PUT"]:
        try:
            body = await request.json()
        except Exception:
            body = None
    
    headers = dict(request.headers)
    
    result = await ProxyService.forward_request(
        path=f"/api/v1/pesagens/{path}",
        method=method,
        body=body,
        headers=headers,
        service="pesagem"
    )
    
    if result["status_code"] == 200:
        return result["content"]
    
    raise HTTPException(
        status_code=result["status_code"],
        detail=result["content"]
    )


# ==================== COTACAO SERVICE ROUTES ====================

@router.api_route("/api/v1/cotacoes", methods=["GET", "POST", "PUT", "DELETE"], response_model=None)
async def proxy_cotacoes_root(request: Request) -> JSONResponse:
    """Roteia requisições para cotacao-service (root path)"""
    method = request.method
    body = None
    
    if method in ["POST", "PUT"]:
        try:
            body = await request.json()
        except Exception:
            body = None
    
    headers = dict(request.headers)
    
    result = await ProxyService.forward_request(
        path="/api/v1/cotacoes",
        method=method,
        body=body,
        headers=headers,
        service="cotacao"
    )
    
    if result["status_code"] == 200:
        return result["content"]
    
    raise HTTPException(
        status_code=result["status_code"],
        detail=result["content"]
    )


@router.api_route("/api/v1/cotacoes/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], response_model=None)
async def proxy_cotacoes(path: str, request: Request) -> JSONResponse:
    """Roteia requisições para cotacao-service"""
    method = request.method
    body = None
    
    if method in ["POST", "PUT"]:
        try:
            body = await request.json()
        except Exception:
            body = None
    
    headers = dict(request.headers)
    
    result = await ProxyService.forward_request(
        path=f"/api/v1/cotacoes/{path}",
        method=method,
        body=body,
        headers=headers,
        service="cotacao"
    )
    
    if result["status_code"] == 200:
        return result["content"]
    
    raise HTTPException(
        status_code=result["status_code"],
        detail=result["content"]
    )


# ==================== SERVICE STATUS ====================

@router.get("/api/status/services", tags=["status"])
async def services_status() -> Dict[str, Any]:
    """Retorna status de saúde de todos os serviços"""
    status_data = await ProxyService.health_check_all()
    
    all_healthy = all(status_data.values())
    
    return {
        "gateway_status": "healthy",
        "services": status_data,
        "all_healthy": all_healthy
    }
