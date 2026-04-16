"""Middleware de Logging Estruturado

Captura:
- method
- path
- status_code
- response_time (em ms)
- client_ip
- service_destination (para proxy requests)
- request_id
"""

import logging
import time
import uuid
import json
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("agrovision.gateway")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging estruturado de requisições"""
    
    # Endpoints excluídos de logging
    EXCLUDED_PATHS = [
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico"
    ]
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Captura e loga informações estruturadas da requisição"""
        
        # Gerar request ID único
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Adicionar request ID em header de response
        request.state.request_id_header = f"X-Request-ID: {request_id}"
        
        # Verificar se é endpoint excluído
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Capturar início da requisição
        start_time = time.time()
        
        # Informações da requisição
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request)
        query_string = request.url.query
        
        # Executar requisição
        try:
            response = await call_next(request)
            status_code = response.status_code
            status_text = response.status_code
        except Exception as e:
            # Se houver erro, logar com status 500
            status_code = 500
            response = Response("Internal Server Error", status_code=500)
            logger.error(
                self._format_log(
                    request_id=request_id,
                    method=method,
                    path=path,
                    status_code=status_code,
                    response_time_ms=0,
                    client_ip=client_ip,
                    error=str(e)
                )
            )
            raise
        
        # Calcular tempo de resposta em ms
        response_time_ms = (time.time() - start_time) * 1000
        
        # Determinar serviço de destino (para proxy requests)
        service_destination = self._get_destination_service(path)
        
        # Log estruturado
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "request_id": request_id,
            "level": self._get_log_level(status_code),
            "method": method,
            "path": path,
            "query": query_string or None,
            "status_code": status_code,
            "response_time_ms": round(response_time_ms, 2),
            "client_ip": client_ip,
        }
        
        # Adicionar serviço de destino se for proxy
        if service_destination:
            log_data["service"] = service_destination
        
        # Logar com nível apropriado
        if status_code >= 500:
            logger.error(json.dumps(log_data))
        elif status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
        
        # Adicionar request_id em header de response
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrair IP do cliente da requisição
        
        Tenta em ordem:
        1. X-Forwarded-For (proxy)
        2. X-Real-IP (nginx)
        3. Connection remoto
        """
        # X-Forwarded-For pode ter múltiplos IPs, pegar o primeiro
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # X-Real-IP
        if "x-real-ip" in request.headers:
            return request.headers["x-real-ip"]
        
        # IP direto da conexão
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _get_destination_service(self, path: str) -> str:
        """Determinar serviço de destino baseado no path
        
        Ex:
        /api/v1/animais/* -> animal-service
        /api/v1/pesagens/* -> pesagem-service
        /api/v1/cotacoes/* -> cotacao-service
        """
        if path.startswith("/api/v1/animais"):
            return "animal-service"
        elif path.startswith("/api/v1/pesagens"):
            return "pesagem-service"
        elif path.startswith("/api/v1/cotacoes"):
            return "cotacao-service"
        return None
    
    def _get_log_level(self, status_code: int) -> str:
        """Determinar nível de log baseado em status code"""
        if status_code >= 500:
            return "ERROR"
        elif status_code >= 400:
            return "WARNING"
        else:
            return "INFO"
    
    def _is_excluded_path(self, path: str) -> bool:
        """Verificar se path está excluído de logging"""
        return any(
            path == excluded or path.startswith(excluded + "/")
            for excluded in self.EXCLUDED_PATHS
        )
    
    def _format_log(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        response_time_ms: float,
        client_ip: str,
        error: str = None
    ) -> str:
        """Formatar log estruturado em JSON"""
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "request_id": request_id,
            "level": self._get_log_level(status_code),
            "method": method,
            "path": path,
            "status_code": status_code,
            "response_time_ms": round(response_time_ms, 2),
            "client_ip": client_ip,
        }
        
        if error:
            log_data["error"] = error
        
        return json.dumps(log_data)
