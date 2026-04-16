"""FastAPI Application - API Gateway"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Health check endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    print("🚀 API Gateway iniciando...")
    yield
    print("🛑 API Gateway encerrando...")


app = FastAPI(
    title="AgroVision API Gateway",
    description="Central de roteamento e autenticação para microserviços",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (primeiro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Estruturado
from app.middlewares.logging import StructuredLoggingMiddleware
app.add_middleware(StructuredLoggingMiddleware)

# Rate Limiting Middleware
from app.middlewares import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)


# Incluir rotas de proxy
from app.api.proxy import router as proxy_router
app.include_router(proxy_router)

# Incluir rotas de agregação
from app.api.aggregation import router as aggregation_router
app.include_router(aggregation_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0"
    }


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": "AgroVision API Gateway",
        "version": "1.0.0",
        "documentation": "/docs",
        "services": {
            "animal": "http://localhost:8000/docs",
            "pesagem": "http://localhost:8001/docs",
            "cotacao": "http://localhost:8002/docs"
        }
    }
