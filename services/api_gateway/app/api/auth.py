"""API Endpoints para Autenticação JWT - FASE 12

Endpoints:
- POST /auth/login: Autenticar com username/password
- POST /auth/refresh: Renovar token com refresh token
- POST /auth/logout: Revogar token
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
    verify_token,
    extract_user_id_from_token,
    revoke_token,
    is_token_revoked
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger("agrovision.auth")

# Banco de dados fictício (em produção, usar banco real)
USERS_DB = {
    "testuser": {
        "user_id": 1,
        "username": "testuser",
        "password_hash": hash_password("testpass"),
        "email": "test@example.com",
        "disabled": False,
    },
    "demo": {
        "user_id": 2,
        "username": "demo",
        "password_hash": hash_password("demo123"),
        "email": "demo@example.com",
        "disabled": False,
    }
}


class LoginRequest(BaseModel):
    """Requisição de login"""
    username: str
    password: str


class RefreshRequest(BaseModel):
    """Requisição de refresh token"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Resposta com tokens"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    """Resposta de login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Autenticar usuário",
    description="Gera tokens de acesso e refresh",
    tags=["Authentication"]
)
async def login(request: LoginRequest):
    """
    Endpoint de login - autenticar com username e password
    
    **Request Body:**
    - `username`: Nome de usuário
    - `password`: Senha
    
    **Response:**
    ```json
    {
        "access_token": "eyJ0eXAi...",
        "refresh_token": "eyJ0eXAi...",
        "token_type": "bearer"
    }
    ```
    
    **Errors:**
    - 401: Credenciais inválidas
    - 400: Usuário desabilitado
    """
    try:
        # Validar entrada
        if not request.username or not request.password:
            logger.warning(f"Login tentado com credenciais vazias")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Buscar usuário
        user = USERS_DB.get(request.username)
        if not user:
            logger.warning(f"Tentativa de login com usuário inválido: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verificar senha
        if not verify_password(request.password, user["password_hash"]):
            logger.warning(f"Senha incorreta para usuário: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verificar se usuário está ativo
        if user.get("disabled", False):
            logger.warning(f"Tentativa de login com usuário desabilitado: {request.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário desabilitado"
            )
        
        # Gerar tokens
        access_token = create_access_token(user["user_id"])
        refresh_token = create_refresh_token(user["user_id"])
        
        logger.info(f"Login bem-sucedido: {request.username} (user_id={user['user_id']})")
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer login"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar token de acesso",
    description="Gera novo access token usando refresh token",
    tags=["Authentication"]
)
async def refresh_access_token(request: RefreshRequest):
    """
    Endpoint de refresh - renovar access token
    
    **Request Body:**
    - `refresh_token`: Token de refresh válido
    
    **Response:**
    ```json
    {
        "access_token": "eyJ0eXAi...",
        "token_type": "bearer"
    }
    ```
    
    **Errors:**
    - 401: Refresh token inválido ou expirado
    """
    try:
        # Validar refresh token
        if not request.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verificar token
        payload = verify_token(request.refresh_token, expected_type="refresh")
        if payload is None:
            logger.warning("Tentativa de refresh com token inválido")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Verificar se token foi revogado
        if is_token_revoked(request.refresh_token):
            logger.warning("Tentativa de refresh com token revogado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token foi revogado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Extrair user_id
        user_id = int(payload["sub"])
        
        # Gerar novo access token
        new_access_token = create_access_token(user_id)
        
        logger.info(f"Token renovado para user_id={user_id}")
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao renovar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao renovar token"
        )


@router.post(
    "/logout",
    summary="Fazer logout",
    description="Revoga o token de acesso",
    tags=["Authentication"]
)
async def logout(authorization: Optional[str] = Header(None)):
    """
    Endpoint de logout - revogar token
    
    **Headers:**
    - `Authorization`: Bearer token
    
    **Response:**
    ```json
    {
        "message": "Logout bem-sucedido"
    }
    ```
    
    **Errors:**
    - 401: Token não fornecido ou inválido
    """
    try:
        # Extrair token do header
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token não fornecido",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validar formato "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Formato de token inválido",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = parts[1]
        
        # Verificar token
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Revogar token
        revoke_token(token)
        
        user_id = payload.get("sub")
        logger.info(f"Logout bem-sucedido: user_id={user_id}")
        
        return {"message": "Logout bem-sucedido"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer logout"
        )
