"""
LLM Service - Main Application
FastAPI service for FPL AI insights using RAG + Llama 3.1 8B
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings
from app.core.rag import get_rag_pipeline
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


class UserContext(BaseModel):
    team_players: Optional[list] = None
    budget: Optional[float] = None
    free_transfers: Optional[int] = None


class QueryRequest(BaseModel):
    query: str
    category: Optional[str] = None
    gameweek: Optional[int] = None
    include_sources: bool = True
    user_context: Optional[UserContext] = None


class QueryResponse(BaseModel):
    answer: str
    sources: Optional[list] = None


@app.post("/api/v1/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Query the RAG system"""
    try:
        rag = get_rag_pipeline()
        
        # Convert user_context to dict if provided
        user_context = None
        if request.user_context:
            user_context = {
                'team_players': request.user_context.team_players,
                'budget': request.user_context.budget,
                'free_transfers': request.user_context.free_transfers,
            }
        
        result = rag.answer_question(
            query=request.query,
            category=request.category,
            gameweek=request.gameweek,
            include_sources=request.include_sources,
            user_context=user_context
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"RAG query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/retrieve")
async def retrieve_only(query: str, top_k: int = 5):
    """Retrieve context without LLM generation"""
    try:
        rag = get_rag_pipeline()
        chunks = rag.retrieve_context(query=query, top_k=top_k)
        return {
            "query": query,
            "count": len(chunks),
            "results": [
                {
                    "text": c['text'][:500] + "..." if len(c['text']) > 500 else c['text'],
                    "metadata": c['metadata'],
                    "relevance": 1 - c['distance']
                }
                for c in chunks
            ]
        }
    except Exception as e:
        logger.error(f"Retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
