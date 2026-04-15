"""
Entry point para rodar o Animal Service
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("ANIMAL_SERVICE_PORT", 8001))
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT", "development") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
