"""Rate Limiting Middleware"""
import redis
import time
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para rate limiting usando Redis"""
    
    def __init__(self, app, redis_url: str = "redis://redis:6379"):
        super().__init__(app)
        self.redis_url = redis_url
        try:
            # Conexão com Redis
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("✅ Redis connected para Rate Limiting")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}. Rate limiting desabilitado")
            self.redis_client = None
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Middleware dispatch"""
        # Se rate limiting desabilitado, passar adiante
        if not settings.rate_limit_enabled or not self.redis_client:
            return await call_next(request)
        
        # Endpoints que não contam para rate limit (status checks)
        excluded_paths = ["/health", "/api/status/services", "/docs", "/openapi.json"]
        if request.url.path in excluded_paths:
            return await call_next(request)
        
        # Extrair IP do cliente
        client_ip = get_client_ip(request)
        
        # Chave de rate limit no Redis
        rate_limit_key = f"rate_limit:{client_ip}"
        
        try:
            # Obter contagem atual
            current_count = get_client_requests_count(self.redis_client, rate_limit_key)
            
            # Verificar se ultrapassou limite
            if current_count >= settings.rate_limit_requests:
                logger.warning(f"⚠️ Rate limit exceeded para {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests",
                        "message": f"Rate limit exceeded: {settings.rate_limit_requests} requests per {settings.rate_limit_seconds} seconds",
                        "retry_after": settings.rate_limit_seconds,
                    },
                    headers={
                        "X-RateLimit-Limit": str(settings.rate_limit_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + settings.rate_limit_seconds),
                        "Retry-After": str(settings.rate_limit_seconds),
                    }
                )
            
            # Incrementar contador
            increment_count = self.redis_client.incr(rate_limit_key)
            
            # Configurar expiry na primeira requisição
            if increment_count == 1:
                self.redis_client.expire(rate_limit_key, settings.rate_limit_seconds)
            
            # Chamar handler
            response = await call_next(request)
            
            # Adicionar headers de rate limit
            response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, settings.rate_limit_requests - increment_count)
            )
            response.headers["X-RateLimit-Reset"] = str(
                int(time.time()) + settings.rate_limit_seconds
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in rate limiting: {e}")
            # Se houver erro, deixar passar (fail open)
            return await call_next(request)


def get_client_ip(request: Request) -> str:
    """Extrair IP do cliente da requisição"""
    # Verificar X-Forwarded-For (proxy)
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # Verificar X-Real-IP
    if "x-real-ip" in request.headers:
        return request.headers["x-real-ip"]
    
    # IP do cliente
    if request.client:
        return request.client.host
    
    # Fallback
    return "unknown"


def get_client_requests_count(
    redis_client: Optional[redis.Redis],
    key: str,
) -> int:
    """Obter quantidade de requisições do cliente"""
    if not redis_client:
        return 0
    
    try:
        count = redis_client.get(key)
        return int(count) if count else 0
    except Exception as e:
        logger.error(f"Error getting rate limit count: {e}")
        return 0


def increment_client_count(
    redis_client: Optional[redis.Redis],
    key: str,
    ttl: int = 60,
) -> int:
    """Incrementar contador de requisições"""
    if not redis_client:
        return 1
    
    try:
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, ttl)
        return count
    except Exception as e:
        logger.error(f"Error incrementing rate limit count: {e}")
        return 0
