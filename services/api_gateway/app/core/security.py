"""Segurança e Autenticação JWT para API Gateway"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Configurações
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "sua-chave-secreta-super-segura-aqui-deve-ter-32-caracteres-minimo"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Context para hash de senhas com bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== Password Hashing ====================

def hash_password(password: str) -> str:
    """
    Gerar hash de senha com bcrypt
    
    Args:
        password: Senha em texto plano
    
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar se senha corresponde ao hash
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Hash da senha
    
    Returns:
        True se corresponde, False caso contrário
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# ==================== JWT Token Operations ====================

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Criar token JWT de acesso
    
    Args:
        user_id: ID do usuário
        expires_delta: Delta de expiração customizado (padrão: 30 minutos)
    
    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Criar token JWT de refresh
    
    Args:
        user_id: ID do usuário
        expires_delta: Delta de expiração customizado (padrão: 7 dias)
    
    Returns:
        Token JWT refresh codificado
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodificar token sem validação (para testes/debugging)
    
    Args:
        token: Token JWT
    
    Returns:
        Payload decodificado ou None se inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (JWTError, Exception):
        return None


def verify_token(
    token: str,
    expected_type: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Verificar e validar token JWT
    
    Args:
        token: Token JWT
        expected_type: Tipo esperado ("access" ou "refresh", opcional)
    
    Returns:
        Payload decodificado se válido, None caso contrário
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar tipo de token se especificado
        if expected_type:
            token_type = payload.get("type")
            if token_type != expected_type:
                return None
        
        return payload
    
    except JWTError as e:
        # Token inválido, expirado ou alterado
        return None
    except Exception as e:
        return None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extrair user_id de um token válido
    
    Args:
        token: Token JWT
    
    Returns:
        User ID ou None se token inválido
    """
    payload = verify_token(token)
    if payload is None:
        return None
    
    try:
        user_id = int(payload.get("sub"))
        return user_id
    except (ValueError, TypeError):
        return None


def is_token_expired(token: str) -> bool:
    """
    Verificar se token está expirado
    
    Args:
        token: Token JWT
    
    Returns:
        True se expirado, False se válido
    """
    payload = get_token_payload(token)
    if payload is None:
        return True
    
    try:
        exp = payload.get("exp")
        if exp is None:
            return True
        
        exp_time = datetime.fromtimestamp(exp)
        now = datetime.utcnow()
        
        return exp_time <= now
    except Exception:
        return True


# ==================== Token Revocation (em memória para MVP) ====================

# Em produção, usar Redis ou banco de dados
_revoked_tokens = set()


def revoke_token(token: str) -> None:
    """
    Revogar um token (adicioná-lo à blacklist)
    
    Args:
        token: Token JWT a revogar
    """
    _revoked_tokens.add(token)


def is_token_revoked(token: str) -> bool:
    """
    Verificar se token foi revogado
    
    Args:
        token: Token JWT
    
    Returns:
        True se revogado, False caso contrário
    """
    return token in _revoked_tokens


def clear_revoked_tokens() -> None:
    """Limpar lista de tokens revogados (para testes)"""
    global _revoked_tokens
    _revoked_tokens.clear()
