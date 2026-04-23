"""API Endpoints para Autenticação JWT - FASE 12

Endpoints:
- POST /auth/register: Registrar novo usuário
- POST /auth/login: Autenticar com username/password
- POST /auth/refresh: Renovar token com refresh token
- POST /auth/logout: Revogar token
- POST /auth/forgot-password: Solicitar reset de senha
- POST /auth/reset-password: Redefinir senha
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel
from typing import Optional, Dict
import logging
import re

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,
    verify_token,
    extract_user_id_from_token,
    revoke_token,
    is_token_revoked,
    create_password_reset_token,
    verify_password_reset_token
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
    "12345678901234": {
        "user_id": 3,
        "username": "12345678901234",
        "password_hash": hash_password("Senha123!"),
        "email": "reset@example.com",
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


class ForgotPasswordRequest(BaseModel):
    """Requisição de esqueci minha senha"""
    cpf_cnpj: str


class ForgotPasswordResponse(BaseModel):
    """Resposta de esqueci minha senha"""
    message: str
    email: str


class ResetPasswordRequest(BaseModel):
    """Requisição de reset de senha"""
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    """Resposta de reset de senha"""
    message: str


class RegisterRequest(BaseModel):
    """Requisição de registro de novo usuário"""
    nome: str
    cpf_cnpj: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    """Resposta de registro"""
    user_id: int
    nome: str
    cpf_cnpj: str
    email: str
    message: str = "Usuário registrado com sucesso"


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validar força da senha
    
    Args:
        password: Senha a validar
    
    Returns:
        Tupla (válida, mensagem_erro)
    """
    if not password:
        return False, "Senha é obrigatória"
    
    if len(password) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "Senha deve conter letra maiúscula"
    
    if not re.search(r'[0-9]', password):
        return False, "Senha deve conter pelo menos um número"
    
    return True, None


def validate_cpf_cnpj_format(cpf_cnpj: str) -> tuple[bool, Optional[str]]:
    """
    Validar formato de CPF ou CNPJ
    
    Args:
        cpf_cnpj: CPF ou CNPJ a validar
    
    Returns:
        Tupla (válido, mensagem_erro)
    """
    if not cpf_cnpj:
        return False, "CPF ou CNPJ é obrigatório"
    
    # Remover caracteres especiais
    clean = re.sub(r'\D', '', cpf_cnpj)
    
    # Validar tamanho (11 para CPF, 14 para CNPJ)
    if len(clean) not in [11, 14]:
        return False, "CPF ou CNPJ inválido"
    
    return True, None


@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário",
    tags=["Authentication"],
    status_code=status.HTTP_201_CREATED
)
async def register(request: RegisterRequest) -> RegisterResponse:
    """
    Endpoint de registro - criar nova conta
    
    **Request Body:**
    - `nome`: Nome completo do usuário
    - `cpf_cnpj`: CPF ou CNPJ (11 ou 14 dígitos)
    - `email`: Email do usuário
    - `password`: Senha (mínimo 8 caracteres, 1 maiúscula, 1 número)
    
    **Response:**
    ```json
    {
        "user_id": 123,
        "nome": "João Silva",
        "cpf_cnpj": "12345678901234",
        "email": "joao@example.com",
        "message": "Usuário registrado com sucesso"
    }
    ```
    
    **Errors:**
    - 400: Dados inválidos ou usuário já existe
    - 500: Erro interno do servidor
    """
    try:
        # Validar CPF/CNPJ
        is_valid, error_msg = validate_cpf_cnpj_format(request.cpf_cnpj)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Limpar CPF/CNPJ (remover caracteres especiais)
        clean_cpf_cnpj = re.sub(r'\D', '', request.cpf_cnpj)
        
        # Verificar se usuário já existe
        if clean_cpf_cnpj in USERS_DB:
            logger.warning(f"Tentativa de registro com CPF/CNPJ já existente: {clean_cpf_cnpj}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF/CNPJ já registrado"
            )
        
        # Verificar email
        for user in USERS_DB.values():
            if user["email"].lower() == request.email.lower():
                logger.warning(f"Tentativa de registro com email já existente: {request.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email já registrado"
                )
        
        # Validar força da senha
        is_strong, error_msg = validate_password_strength(request.password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Validar nome
        if not request.nome or len(request.nome.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome deve ter no mínimo 3 caracteres"
            )
        
        # Validar email
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email inválido"
            )
        
        # Criar novo usuário
        new_user_id = max([user["user_id"] for user in USERS_DB.values()]) + 1 if USERS_DB else 1
        
        USERS_DB[clean_cpf_cnpj] = {
            "user_id": new_user_id,
            "username": clean_cpf_cnpj,
            "password_hash": hash_password(request.password),
            "email": request.email,
            "nome": request.nome,
            "disabled": False,
        }
        
        logger.info(f"Novo usuário registrado: {clean_cpf_cnpj} (user_id={new_user_id})")
        
        return RegisterResponse(
            user_id=new_user_id,
            nome=request.nome,
            cpf_cnpj=clean_cpf_cnpj,
            email=request.email,
            message="Usuário registrado com sucesso"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar usuário"
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Autenticar usuário",
    description="Gera tokens de acesso e refresh",
    tags=["Authentication"]
)
async def login(request: LoginRequest) -> LoginResponse:
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
async def refresh_access_token(request: RefreshRequest) -> TokenResponse:
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
async def logout(authorization: Optional[str] = Header(None)) -> Dict[str, str]:
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


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Solicitar reset de senha",
    description="Envia email com link para resetar senha",
    tags=["Authentication"]
)
async def forgot_password(request: ForgotPasswordRequest) -> ForgotPasswordResponse:
    """
    Endpoint de forgot password - solicitar reset de senha
    
    **Request Body:**
    - `cpf_cnpj`: CPF ou CNPJ do usuário
    
    **Response:**
    ```json
    {
        "message": "Email de recuperação enviado",
        "email": "user@example.com"
    }
    ```
    
    **Errors:**
    - 400: CPF/CNPJ inválido
    - 404: Usuário não encontrado
    """
    try:
        # Validar formato de CPF/CNPJ
        is_valid, error_msg = validate_cpf_cnpj_format(request.cpf_cnpj)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Buscar usuário (em produção, buscar no banco de dados)
        # Para este MVP, vamos simular buscando nos USERS_DB
        user = USERS_DB.get(request.cpf_cnpj)
        
        if not user:
            # Por segurança, não informar se usuário não existe
            # Sempre retornar sucesso
            logger.warning(f"Tentativa de forgot password para usuário inexistente: {request.cpf_cnpj}")
            return ForgotPasswordResponse(
                message="Email de recuperação enviado",
                email="****@example.com"
            )
        
        # Gerar token de reset
        reset_token = create_password_reset_token(request.cpf_cnpj)
        
        # Em produção, enviar email real com link:
        # reset_url = f"https://agrovision.com/reset-password?token={reset_token}"
        # send_email(user["email"], reset_url)
        
        # Para MVP, apenas logar
        logger.info(f"Reset password token gerado para: {request.cpf_cnpj}")
        logger.debug(f"Reset token: {reset_token}")
        
        # Mascarar email para resposta
        email = user.get("email", "****@example.com")
        masked_email = f"{email[:2]}***@{email.split('@')[1]}" if "@" in email else "****@example.com"
        
        return ForgotPasswordResponse(
            message="Email de recuperação enviado",
            email=masked_email
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar forgot password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar solicitação"
        )


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    summary="Redefinir senha",
    description="Redefine a senha usando token de reset",
    tags=["Authentication"]
)
async def reset_password(request: ResetPasswordRequest) -> ResetPasswordResponse:
    """
    Endpoint de reset password - redefinir senha
    
    **Request Body:**
    - `token`: Token de reset obtido via email
    - `new_password`: Nova senha (mínimo 8 caracteres, 1 maiúscula, 1 número)
    
    **Response:**
    ```json
    {
        "message": "Senha alterada com sucesso"
    }
    ```
    
    **Errors:**
    - 400: Senha fraca
    - 401: Token inválido ou expirado
    """
    try:
        # Validar força da senha
        is_strong, error_msg = validate_password_strength(request.new_password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Verificar token de reset
        try:
            cpf_cnpj = verify_password_reset_token(request.token)
        except ValueError as e:
            logger.warning(f"Token de reset inválido: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        
        # Buscar usuário
        user = USERS_DB.get(cpf_cnpj)
        if not user:
            logger.warning(f"Usuário não encontrado ao resetar senha: {cpf_cnpj}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Atualizar senha
        new_password_hash = hash_password(request.new_password)
        user["password_hash"] = new_password_hash
        
        logger.info(f"Senha resetada com sucesso para: {cpf_cnpj}")
        
        return ResetPasswordResponse(
            message="Senha alterada com sucesso"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao resetar senha"
        )
