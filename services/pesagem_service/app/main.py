"""
FastAPI Application Factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.init_db import init_db
from app.api import router

logger = logging.getLogger(__name__)

# Inicializar banco de dados com retry
try:
    init_db(max_retries=5, retry_interval=2)
except Exception as e:
    logger.error(f"Falha ao inicializar banco de dados: {e}")
    raise

# Criar app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
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
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
