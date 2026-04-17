from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import router
from app.core.config import settings
from app.core.init_db import init_db

logger = logging.getLogger(__name__)

# Inicializar banco de dados com retry
try:
    init_db(max_retries=5, retry_interval=2)
except Exception as e:
    logger.error(f"Falha ao inicializar banco de dados: {e}")
    raise

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Serviço de Cotação de Preços de Arroba"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(router)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/")
def root():
    """Endpoint raiz"""
    return {"message": f"Bem-vindo ao {settings.APP_NAME}"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
