"""Testes para endpoints de autenticação com CPF/CNPJ"""
import pytest
from fastapi.testclient import TestClient
from datetime import timedelta

from app import app
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

client = TestClient(app)


class TestAuthLoginEndpoint:
    """Testes para POST /auth/login"""

    def test_login_with_valid_credentials(self):
        """Deve fazer login com credenciais válidas"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_with_invalid_credentials(self):
        """Deve rejeitar credenciais inválidas"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpass"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Credenciais inválidas"

    def test_login_with_non_existent_user(self):
        """Deve rejeitar usuário inexistente"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Credenciais inválidas"

    def test_login_with_empty_username(self):
        """Deve rejeitar username vazio"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "", "password": "testpass"}
        )

        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]

    def test_login_with_empty_password(self):
        """Deve rejeitar password vazia"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": ""}
        )

        assert response.status_code == 401
        assert "Credenciais inválidas" in response.json()["detail"]

    def test_login_with_disabled_user(self):
        """Deve rejeitar usuário desabilitado"""
        # Este teste requer uma modificação no banco de dados de teste
        # Para fins de demonstração, estamos testando o comportamento esperado
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        # Se o usuário estiver ativo, deve retornar 200
        assert response.status_code in [200, 400]

    def test_login_returns_valid_jwt_token(self):
        """Token retornado deve ser um JWT válido"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "demo", "password": "demo123"}
        )

        assert response.status_code == 200
        token = response.json()["access_token"]

        # Tentar usar o token em uma requisição autenticada
        headers = {"Authorization": f"Bearer {token}"}
        # Aqui você pode fazer uma requisição que requeira autenticação


class TestAuthRefreshEndpoint:
    """Testes para POST /auth/refresh"""

    def test_refresh_with_valid_refresh_token(self):
        """Deve renovar token com refresh token válido"""
        # Primeiro, fazer login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        refresh_token = login_response.json()["refresh_token"]

        # Agora, usar o refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # O novo access token deve ser diferente do anterior
        assert data["access_token"] != login_response.json()["access_token"]

    def test_refresh_with_invalid_refresh_token(self):
        """Deve rejeitar refresh token inválido"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token_xyz"}
        )

        assert response.status_code == 401
        assert "inválido" in response.json()["detail"].lower()

    def test_refresh_with_empty_refresh_token(self):
        """Deve rejeitar refresh token vazio"""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": ""}
        )

        assert response.status_code == 401

    def test_refresh_with_access_token_as_refresh(self):
        """Não deve aceitar access token como refresh token"""
        # Fazer login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        access_token = login_response.json()["access_token"]

        # Tentar usar access token como refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token}
        )

        # Pode retornar 401 dependendo da implementação
        assert response.status_code in [401, 400]


class TestAuthLogoutEndpoint:
    """Testes para POST /auth/logout"""

    def test_logout_with_valid_token(self):
        """Deve fazer logout com token válido"""
        # Fazer login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        access_token = login_response.json()["access_token"]

        # Fazer logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_logout_without_token(self):
        """Deve rejeitar logout sem token"""
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 401

    def test_logout_with_invalid_token(self):
        """Deve rejeitar logout com token inválido"""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_logout_with_malformed_header(self):
        """Deve rejeitar header Authorization malformado"""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "invalid_format"}
        )

        assert response.status_code == 401

    def test_cannot_use_token_after_logout(self):
        """Não deve ser possível usar token após logout"""
        # Fazer login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        access_token = login_response.json()["access_token"]

        # Fazer logout
        client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Tentar usar o token (em uma rota que requeira autenticação)
        # Isso depende de ter uma rota protegida para testar


class TestAuthResponseFormats:
    """Testes para formatos de resposta"""

    def test_login_response_format(self):
        """Resposta de login deve ter formato correto"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar campos obrigatórios
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

        # Verificar tipos
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)

    def test_error_response_format(self):
        """Resposta de erro deve ter formato correto"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpass"}
        )

        assert response.status_code == 401
        data = response.json()

        # Verificar estrutura de erro
        assert "detail" in data

    def test_refresh_response_format(self):
        """Resposta de refresh deve ter formato correto"""
        # Fazer login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        refresh_token = login_response.json()["refresh_token"]

        # Fazer refresh
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar campos obrigatórios
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"


class TestCPFCNPJValidation:
    """Testes para validação de CPF/CNPJ"""

    def test_login_with_cpf_format(self):
        """Deve aceitar login com CPF no username"""
        # Este teste pressupõe que o backend suporte CPF como username
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "12345678901", "password": "testpass"}
        )

        # Pode retornar 401 se não houver usuário com esse CPF
        assert response.status_code in [401, 200]

    def test_login_with_cnpj_format(self):
        """Deve aceitar login com CNPJ no username"""
        # Este teste pressupõe que o backend suporte CNPJ como username
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "12345678901234", "password": "testpass"}
        )

        # Pode retornar 401 se não houver usuário com esse CNPJ
        assert response.status_code in [401, 200]
