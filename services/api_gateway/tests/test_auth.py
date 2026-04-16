"""Testes de autenticação JWT"""
import pytest
from datetime import timedelta
from app.core import (
    create_access_token,
    verify_token,
    verify_password,
    get_password_hash,
    TokenData
)


class TestPasswordHashing:
    """Testes de hash de senhas"""
    
    def test_hash_password_creates_hash(self):
        """Deve criar hash da senha"""
        password = "senha123"
        hashed = get_password_hash(password)
        assert hashed != password
    
    def test_verify_password_correct(self):
        """Deve verificar senha correta"""
        password = "senha123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Deve rejeitar senha incorreta"""
        password = "senha123"
        hashed = get_password_hash(password)
        assert verify_password("wrongpass", hashed) is False
    
    def test_same_password_different_hashes(self):
        """Mesma senha deve gerar hashes diferentes"""
        password = "senha123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTToken:
    """Testes de tokens JWT"""
    
    def test_create_access_token_returns_string(self):
        """Deve retornar string de token"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_custom_expiration(self):
        """Deve criar token com expiração customizada"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        assert isinstance(token, str)
    
    def test_verify_valid_token(self):
        """Deve verificar token válido"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        token_data = verify_token(token)
        assert token_data is not None
        assert token_data.username == "testuser"
    
    def test_verify_invalid_token_returns_none(self):
        """Deve retornar None para token inválido"""
        token = "invalid_token_xyz"
        result = verify_token(token)
        assert result is None
    
    def test_verify_token_with_scopes(self):
        """Deve verificar token com scopes"""
        data = {"sub": "testuser", "scopes": ["read", "write"]}
        token = create_access_token(data)
        token_data = verify_token(token)
        assert token_data is not None
        assert "read" in token_data.scopes
        assert "write" in token_data.scopes
    
    def test_token_includes_username(self):
        """Token deve incluir username"""
        data = {"sub": "johndoe"}
        token = create_access_token(data)
        token_data = verify_token(token)
        assert token_data.username == "johndoe"


class TestTokenData:
    """Testes do modelo TokenData"""
    
    def test_token_data_creation(self):
        """Deve criar TokenData"""
        token_data = TokenData(username="testuser", scopes=["read"])
        assert token_data.username == "testuser"
        assert token_data.scopes == ["read"]
    
    def test_token_data_optional_username(self):
        """Username deve ser opcional"""
        token_data = TokenData(scopes=["read"])
        assert token_data.username is None
        assert token_data.scopes == ["read"]
    
    def test_token_data_default_scopes(self):
        """Scopes deve ter valor padrão"""
        token_data = TokenData(username="user")
        assert token_data.scopes == []
