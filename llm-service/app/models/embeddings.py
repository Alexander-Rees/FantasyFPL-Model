"""
Embedding Model - bge-m3 for semantic search
"""
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from typing import Union, List
import logging
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """BGE-M3 embedding model for semantic search"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize embedding model
        
        Args:
            model_name: Model identifier (default from settings)
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.model = None
        self._loaded = False
    
    def load_model(self):
        """Load embedding model (lazy loading)"""
        if self._loaded:
            return
        
        try:
            logger.info(f"Loading embedding model {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("✅ Embedding model loaded successfully")
        except Exception as e:
            logger.warning(f"Embedding model load failed ({e}); falling back to random embeddings.")
            self.model = None
            import numpy as np
            self.random_state = np.random.RandomState(42) # Initialize random state for deterministic fallback
    
    def _embed(self, texts: list[str]) -> np.ndarray:
        """Internal method to get embeddings, handling fallback."""
        if self.model is not None:
            return self.model.encode(texts, batch_size=self.batch_size, convert_to_numpy=True)
        else:
            # Generate deterministic random vectors for each text
            if self.random_state is None: # Should not happen if load_model was called
                self.random_state = np.random.RandomState(42)
            return self.random_state.rand(len(texts), self.fallback_dim)

    def encode(self, texts: Union[List[str], str], batch_size: int = 32) -> np.ndarray:
        """
        Encode texts to embeddings
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        if not self._loaded:
            self.load_model()
        
        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
        
        if self.model is None:
            logger.error("Embedding model not loaded. Cannot encode texts.")
            raise RuntimeError("Embedding model not available. Please check model loading.")
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 10,
                convert_to_numpy=True
            )
            return embeddings
            
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a single query
        
        Args:
            query: Query text
            
        Returns:
            Query embedding
        """
        return self.encode(query)[0]
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._loaded:
            logger.info("Unloading embedding model")


# Global embedding instance (singleton)
_embedding_instance = None


def get_embedding_model() -> EmbeddingModel:
    """Get global embedding model instance (singleton pattern)"""
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = EmbeddingModel()
    return _embedding_instance
