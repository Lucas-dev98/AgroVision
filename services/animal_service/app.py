"""
FastAPI Application - Animal Service
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from shared.database import init_db

# Carregar variáveis de ambiente
load_dotenv()


# Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia startup e shutdown da aplicação"""
    # Startup
    print("🚀 Starting Animal Service...")
    init_db()  # Criar tabelas se não existem
    print("✅ Animal Service started!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Animal Service...")


# Criar app FastAPI
app = FastAPI(
    title="Animal Service",
    description="Microserviço para gerenciamento de animais",
    version="1.0.0",
    lifespan=lifespan
)


# Health check
@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    return {
        "status": "alive",
        "service": "animal-service",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Animal Service API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }
