"""
LLM Service - Main Application
FastAPI service for FPL AI insights using RAG + Llama 3.1 8B
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION,
    description="FPL AI Assistant - RAG + LLM Service"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security: Internal API token validation
async def verify_internal_token(x_internal_token: str = Header(None)):
    """Verify internal API token for service-to-service auth"""
    if x_internal_token != settings.INTERNAL_API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid internal token")
    return x_internal_token


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION
    }


@app.get("/api/v1/info")
async def service_info():
    """Service information"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "llm_model": settings.LLM_MODEL_NAME,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "vector_db": settings.VECTOR_DB_PATH,
        "status": "ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
