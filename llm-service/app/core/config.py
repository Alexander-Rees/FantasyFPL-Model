"""
LLM Service Configuration
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "fpl-llm-service"
    VERSION: str = "0.1.0"
    HOST: str = "0.0.0.0"
    PORT: int = 5002
    
    # LLM Model
    LLM_MODEL_NAME: str = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
    LLM_MODEL_PATH: str = "data/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    LLM_HF_MODEL_NAME: str = "Qwen/Qwen2.5-1.5B-Instruct"  # Fallback PyTorch model
    MAX_NEW_TOKENS: int = 1024
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    
    # LLM API Settings (for external API services)
    LLM_API_PROVIDER: str = ""  # 'openai', 'anthropic', 'groq', 'huggingface', or empty for local
    LLM_API_KEY: str = ""  # API key for the provider (optional for some free tiers)
    LLM_API_MODEL: str = "gpt-4o-mini"  # Default model
    # Groq free models: llama-3.1-8b-instant, llama-3.1-70b-versatile, mixtral-8x7b-32768
    # Hugging Face: meta-llama/Meta-Llama-3-8B-Instruct, mistralai/Mistral-7B-Instruct-v0.2
    
    # Embedding Model (all-MiniLM-L6-v2 is small & fast, bge-m3 is better but slower)
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    
    # Vector Store
    VECTOR_DB_PATH: str = "data/vector_db"
    COLLECTION_NAME: str = "fpl_articles"
    
    # RAG Settings
    CHUNK_SIZE: int = 300
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 5
    
    # Scraper Data
    SCRAPED_DATA_PATH: str = "scraper/data/raw/scraped"
    
    # Security
    INTERNAL_API_TOKEN: str = "dev-internal-token"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
