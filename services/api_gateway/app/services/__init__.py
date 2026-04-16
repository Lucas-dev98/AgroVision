"""Serviço de proxy reverso para rotear requisições para os microserviços"""
import httpx
from typing import Optional, Dict, Any
from fastapi import Request
from app.config import settings

# Cliente HTTP assíncrono
client = httpx.AsyncClient(timeout=30.0)


class ProxyService:
    """Serviço de proxy reverso"""
    
    @staticmethod
    async def forward_request(
        path: str,
        method: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        service: str = "animal"
    ) -> Dict[str, Any]:
        """
        Roteia requisição para serviço
        
        Args:
            path: Caminho da requisição (ex: /api/v1/animais)
            method: Método HTTP (GET, POST, PUT, DELETE)
            body: Corpo da requisição (JSON)
            headers: Headers adicionais
            service: Serviço destino (animal, pesagem, cotacao)
        
        Returns:
            Dict com status_code, content, headers
        """
        # Determinar URL base do serviço
        service_urls = {
            "animal": settings.animal_service_url,
            "pesagem": settings.pesagem_service_url,
            "cotacao": settings.cotacao_service_url,
        }
        
        base_url = service_urls.get(service)
        if not base_url:
            raise ValueError(f"Serviço desconhecido: {service}")
        
        url = f"{base_url}{path}"
        
        # Preparar headers
        forward_headers = headers or {}
        # Remover headers que não devem ser reenviados
        forward_headers.pop("host", None)
        
        try:
            # Fazer requisição
            response = await client.request(
                method=method,
                url=url,
                json=body,
                headers=forward_headers,
                follow_redirects=True
            )
            
            return {
                "status_code": response.status_code,
                "content": response.json() if response.text else None,
                "headers": dict(response.headers),
            }
        except httpx.ConnectError:
            return {
                "status_code": 503,
                "content": {"error": f"Serviço {service} indisponível"},
                "headers": {},
            }
        except httpx.TimeoutException:
            return {
                "status_code": 504,
                "content": {"error": f"Timeout ao conectar com serviço {service}"},
                "headers": {},
            }
        except Exception as e:
            return {
                "status_code": 500,
                "content": {"error": f"Erro ao rotear requisição: {str(e)}"},
                "headers": {},
            }
    
    @staticmethod
    async def health_check_service(service: str) -> bool:
        """
        Verifica se um serviço está disponível
        
        Args:
            service: Nome do serviço
        
        Returns:
            True se serviço está saudável, False caso contrário
        """
        service_urls = {
            "animal": settings.animal_service_url,
            "pesagem": settings.pesagem_service_url,
            "cotacao": settings.cotacao_service_url,
        }
        
        base_url = service_urls.get(service)
        if not base_url:
            return False
        
        try:
            response = await client.get(f"{base_url}/health", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
    
    @staticmethod
    async def health_check_all() -> Dict[str, bool]:
        """
        Verifica saúde de todos os serviços
        
        Returns:
            Dict com status de cada serviço
        """
        return {
            "animal": await ProxyService.health_check_service("animal"),
            "pesagem": await ProxyService.health_check_service("pesagem"),
            "cotacao": await ProxyService.health_check_service("cotacao"),
        }
