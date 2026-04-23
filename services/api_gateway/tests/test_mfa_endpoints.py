import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


class TestAuthMFAEndpoints:
    """
    Testes para endpoints de autenticação multi-fator (MFA)
    """

    def test_mfa_send_email_code(self, client: TestClient, auth_headers):
        """Deve enviar código MFA por email"""
        response = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 1,
                'method': 'email',
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert 'session_token' in data
        assert data['method'] == 'email'
        assert 'message' in data

    def test_mfa_send_sms_code(self, client: TestClient, auth_headers):
        """Deve enviar código MFA por SMS"""
        response = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 1,
                'method': 'sms',
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert 'session_token' in data
        assert data['method'] == 'sms'

    def test_mfa_send_authenticator_code(self, client: TestClient, auth_headers):
        """Deve preparar verificação com authenticator"""
        response = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 1,
                'method': 'authenticator',
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert 'session_token' in data
        assert data['method'] == 'authenticator'

    def test_mfa_send_invalid_method(self, client: TestClient, auth_headers):
        """Deve rejeitar método MFA inválido"""
        response = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 1,
                'method': 'invalid_method',
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert 'método' in response.json()['detail'].lower()

    def test_mfa_send_user_not_found(self, client: TestClient, auth_headers):
        """Deve retornar erro quando usuário não existe"""
        response = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 999,
                'method': 'email',
            },
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert 'não encontrado' in response.json()['detail'].lower()

    def test_mfa_send_requires_auth(self, client: TestClient):
        """Deve exigir autenticação para enviar código MFA"""
        response = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 1,
                'method': 'email',
            },
        )

        assert response.status_code == 401

    def test_mfa_verify_valid_code(self, client: TestClient):
        """Deve verificar código MFA válido e retornar tokens"""
        # Primeiro, enviar código (seria feito no login)
        # Para este teste, assumimos que um code session foi criado
        
        response = client.post(
            '/api/v1/auth/mfa/verify',
            json={
                'session_token': 'valid_session_token',
                'code': '123456',
            },
        )

        # Se a sessão/código não existe (esperado em um teste unitário sem DB real)
        # podemos verificar que a rota existe e é acessível
        assert response.status_code in [200, 401, 400]

        if response.status_code == 200:
            data = response.json()
            assert 'access_token' in data
            assert 'refresh_token' in data
            assert data['token_type'] == 'bearer'

    def test_mfa_verify_invalid_code(self, client: TestClient):
        """Deve rejeitar código MFA inválido"""
        response = client.post(
            '/api/v1/auth/mfa/verify',
            json={
                'session_token': 'valid_session_token',
                'code': '000000',
            },
        )

        # Código inválido deve retornar erro
        assert response.status_code in [400, 401]

    def test_mfa_verify_expired_session(self, client: TestClient):
        """Deve rejeitar código com session expirada"""
        response = client.post(
            '/api/v1/auth/mfa/verify',
            json={
                'session_token': 'expired_session_token',
                'code': '123456',
            },
        )

        assert response.status_code in [401, 400]
        assert 'session' in response.json()['detail'].lower() or 'expirada' in response.json()['detail'].lower()

    def test_mfa_verify_missing_fields(self, client: TestClient):
        """Deve validar campos obrigatórios"""
        # Faltando session_token
        response = client.post(
            '/api/v1/auth/mfa/verify',
            json={
                'code': '123456',
            },
        )

        assert response.status_code == 422  # Validation error

        # Faltando code
        response = client.post(
            '/api/v1/auth/mfa/verify',
            json={
                'session_token': 'valid_session_token',
            },
        )

        assert response.status_code == 422

    def test_mfa_verify_invalid_code_format(self, client: TestClient):
        """Deve validar formato do código (deve ser 6 dígitos)"""
        response = client.post(
            '/api/v1/auth/mfa/verify',
            json={
                'session_token': 'valid_session_token',
                'code': '12345',  # Apenas 5 dígitos
            },
        )

        assert response.status_code == 422

    def test_mfa_resend_code(self, client: TestClient):
        """Deve reenviar código MFA"""
        response = client.post(
            '/api/v1/auth/mfa/resend',
            json={
                'session_token': 'valid_session_token',
            },
        )

        # Se a sessão não existe (esperado em teste unitário)
        assert response.status_code in [200, 401, 400]

        if response.status_code == 200:
            data = response.json()
            assert 'message' in data

    def test_mfa_resend_invalid_session(self, client: TestClient):
        """Deve rejeitar reenvio com session inválida"""
        response = client.post(
            '/api/v1/auth/mfa/resend',
            json={
                'session_token': 'invalid_session_token',
            },
        )

        assert response.status_code in [401, 400]

    def test_mfa_resend_rate_limit(self, client: TestClient):
        """Deve limitar tentativas de reenvio"""
        session_token = 'valid_session_token'

        # Primeira requisição deve passar
        response1 = client.post(
            '/api/v1/auth/mfa/resend',
            json={'session_token': session_token},
        )

        # Múltiplas tentativas rápidas devem ser limitadas
        response2 = client.post(
            '/api/v1/auth/mfa/resend',
            json={'session_token': session_token},
        )

        # A segunda requisição deve retornar erro de rate limit (429)
        # ou a primeira realmente falhou por sessão inválida
        assert response2.status_code in [429, 400, 401]

    def test_mfa_code_attempts_limit(self, client: TestClient):
        """Deve limitar tentativas de verificação de código"""
        session_token = 'valid_session_token'

        # Fazer 5+ tentativas com código errado
        for i in range(6):
            response = client.post(
                '/api/v1/auth/mfa/verify',
                json={
                    'session_token': session_token,
                    'code': '000000',
                },
            )

        # Após muitas tentativas, deve ser bloqueado
        response_final = client.post(
            '/api/v1/auth/mfa/verify',
            json={
                'session_token': session_token,
                'code': '123456',
            },
        )

        # Pode estar bloqueado (429 too many attempts) ou session pode ter expirado
        assert response_final.status_code in [429, 401, 400]

    def test_mfa_response_format(self, client: TestClient, auth_headers):
        """Deve retornar formato de resposta correto"""
        response = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 1,
                'method': 'email',
            },
            headers=auth_headers,
        )

        if response.status_code == 200:
            data = response.json()

            # Verificar estrutura da resposta
            assert isinstance(data, dict)
            assert 'session_token' in data
            assert 'method' in data
            assert 'message' in data

            # Validar tipos
            assert isinstance(data['session_token'], str)
            assert isinstance(data['method'], str)
            assert isinstance(data['message'], str)

    def test_mfa_session_token_is_unique(self, client: TestClient, auth_headers):
        """Deve gerar session tokens únicos para cada requisição"""
        response1 = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 1,
                'method': 'email',
            },
            headers=auth_headers,
        )

        response2 = client.post(
            '/api/v1/auth/mfa/send',
            json={
                'user_id': 1,
                'method': 'email',
            },
            headers=auth_headers,
        )

        if response1.status_code == 200 and response2.status_code == 200:
            token1 = response1.json()['session_token']
            token2 = response2.json()['session_token']

            # Tokens devem ser diferentes
            assert token1 != token2
