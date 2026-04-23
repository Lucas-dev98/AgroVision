"""Testes para endpoints de recuperação de senha"""
import pytest
from fastapi.testclient import TestClient
from datetime import timedelta, datetime, timezone
import json

from app import app
from app.core.security import create_password_reset_token, verify_password_reset_token

client = TestClient(app)


class TestForgotPasswordEndpoint:
    """Testes para POST /auth/forgot-password"""

    def test_forgot_password_with_valid_cpf(self):
        """Deve enviar token de reset para CPF válido"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"cpf_cnpj": "12345678901234"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Email de recuperação enviado"
        assert data["email"] is not None
        assert "@" in data["email"]

    def test_forgot_password_with_valid_cnpj(self):
        """Deve enviar token de reset para CNPJ válido"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"cpf_cnpj": "12345678901234"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Email de recuperação enviado"

    def test_forgot_password_with_invalid_cpf_format(self):
        """Deve rejeitar CPF/CNPJ com formato inválido"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"cpf_cnpj": "123"}  # Muito curto
        )

        assert response.status_code == 400
        assert "CPF ou CNPJ inválido" in response.json()["detail"]

    def test_forgot_password_with_nonexistent_user(self):
        """Deve retornar mensagem genérica para usuário inexistente"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"cpf_cnpj": "99999999999999"}
        )

        # Por segurança, sempre retorna sucesso mesmo se usuário não existe
        assert response.status_code == 200
        assert "Email de recuperação enviado" in response.json()["message"]

    def test_forgot_password_with_empty_cpf(self):
        """Deve rejeitar CPF/CNPJ vazio"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"cpf_cnpj": ""}
        )

        assert response.status_code == 400
        assert "CPF ou CNPJ é obrigatório" in response.json()["detail"]

    def test_forgot_password_missing_cpf_field(self):
        """Deve rejeitar quando campo CPF/CNPJ está faltando"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={}
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_forgot_password_rate_limiting(self):
        """Deve limitar requisições de forgot password por usuário"""
        cpf = "12345678901234"
        
        # Primeira requisição deve passar
        response1 = client.post(
            "/api/v1/auth/forgot-password",
            json={"cpf_cnpj": cpf}
        )
        assert response1.status_code == 200
        
        # Segunda requisição imediata pode ser limitada (depende da implementação)
        # Isso é opcional mas recomendado


class TestResetPasswordEndpoint:
    """Testes para POST /auth/reset-password"""

    def test_reset_password_with_valid_token(self):
        """Deve resetar senha com token válido"""
        # Primeiro, criar um token válido
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "NovaSenha123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Senha alterada com sucesso"

    def test_reset_password_with_invalid_token(self):
        """Deve rejeitar token inválido"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "token_invalido_xyz",
                "new_password": "NovaSenha123!"
            }
        )

        assert response.status_code == 401
        assert "Token inválido ou expirado" in response.json()["detail"]

    def test_reset_password_with_expired_token(self):
        """Deve rejeitar token expirado"""
        # Criar token com expiração no passado
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=-1)  # Negativo = passou
        )
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "NovaSenha123!"
            }
        )

        assert response.status_code == 401
        assert "Token inválido ou expirado" in response.json()["detail"]

    def test_reset_password_with_weak_password(self):
        """Deve rejeitar senha fraca"""
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "123"  # Muito curta
            }
        )

        assert response.status_code == 400
        assert "Senha deve ter no mínimo 8 caracteres" in response.json()["detail"]

    def test_reset_password_without_uppercase(self):
        """Deve rejeitar senha sem letra maiúscula"""
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "senha123!"  # Sem maiúscula
            }
        )

        assert response.status_code == 400
        assert "Senha deve conter letra maiúscula" in response.json()["detail"]

    def test_reset_password_without_number(self):
        """Deve rejeitar senha sem número"""
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "SenhaForte!"  # Sem número
            }
        )

        assert response.status_code == 400
        assert "Senha deve conter pelo menos um número" in response.json()["detail"]

    def test_reset_password_with_empty_password(self):
        """Deve rejeitar password vazia"""
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": ""
            }
        )

        assert response.status_code == 400

    def test_reset_password_enables_login(self):
        """Deve permitir login após reset de senha"""
        cpf = "12345678901234"
        new_password = "NovaSenha123!"
        
        # Criar token
        token = create_password_reset_token(
            cpf_cnpj=cpf,
            expires_delta=timedelta(hours=1)
        )
        
        # Reset password
        reset_response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": new_password
            }
        )
        assert reset_response.status_code == 200
        
        # Tentar fazer login com nova senha
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": cpf,
                "password": new_password
            }
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_reset_password_missing_token(self):
        """Deve rejeitar quando token está faltando"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "new_password": "NovaSenha123!"
            }
        )

        assert response.status_code == 422

    def test_reset_password_missing_password(self):
        """Deve rejeitar quando password está faltando"""
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token
            }
        )

        assert response.status_code == 422


class TestPasswordResetTokenGeneration:
    """Testes para geração e validação de tokens de reset"""

    def test_create_password_reset_token(self):
        """Deve criar token válido"""
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=1)
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_password_reset_token(self):
        """Deve verificar token válido"""
        cpf = "12345678901234"
        token = create_password_reset_token(
            cpf_cnpj=cpf,
            expires_delta=timedelta(hours=1)
        )
        
        decoded_cpf = verify_password_reset_token(token)
        assert decoded_cpf == cpf

    def test_verify_expired_password_reset_token(self):
        """Deve rejeitar token expirado"""
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=-1)  # Passado
        )
        
        with pytest.raises(ValueError, match="Token expirado"):
            verify_password_reset_token(token)

    def test_verify_invalid_password_reset_token(self):
        """Deve rejeitar token inválido"""
        with pytest.raises(ValueError):
            verify_password_reset_token("token_completamente_invalido")

    def test_verify_tampered_password_reset_token(self):
        """Deve rejeitar token modificado"""
        token = create_password_reset_token(
            cpf_cnpj="12345678901234",
            expires_delta=timedelta(hours=1)
        )
        
        # Modificar token
        tampered_token = token[:-5] + "xxxxx"
        
        with pytest.raises(ValueError):
            verify_password_reset_token(tampered_token)
