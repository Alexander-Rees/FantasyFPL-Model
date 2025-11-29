"""
Vector Store - Chroma DB for RAG
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.models.embeddings import get_embedding_model
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class VectorStore:
    """Chroma vector store for FPL articles"""
    
    def __init__(self, persist_directory: str = None):
        """
        Initialize Chroma vector store
        
        Args:
            persist_directory: Directory to persist vector DB
        """
        self.persist_directory = persist_directory or settings.VECTOR_DB_PATH
        self.collection_name = settings.COLLECTION_NAME
        self.client = None
        self.collection = None
        self.embedding_model = get_embedding_model()
    
    def initialize(self):
        """Initialize Chroma client and collection"""
        if self.client is not None:
            return
        
        logger.info(f"Initializing Chroma DB at {self.persist_directory}")
        
        # Create persist directory
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "FPL expert articles for RAG"}
        )
        
        logger.info(f"✅ Chroma initialized with {self.collection.count()} documents")
    
    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str]
    ):
        """
        Add documents to vector store
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dicts
            ids: List of unique document IDs
        """
        if self.collection is None:
            self.initialize()
        
        # Load embedding model
        self.embedding_model.load_model()
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedding_model.encode(documents)
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings.tolist()
        )
        
        logger.info(f"✅ Added {len(documents)} documents to vector store")
    
    def query(
        self,
        query_text: str,
        n_results: int = None,
        where: dict = None
    ) -> dict:
        """
        Query vector store for similar documents
        
        Args:
            query_text: Query string
            n_results: Number of results to return (default from settings)
            where: Metadata filter (e.g., {"category": "captaincy"})
            
        Returns:
            Dict with keys: ids, documents, metadatas, distances
        """
        if self.collection is None:
            self.initialize()
        
        # Load embedding model
        self.embedding_model.load_model()
        
        n_results = n_results or settings.TOP_K_RETRIEVAL
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode_query(query_text)
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def get_count(self) -> int:
        """Get number of documents in collection"""
        if self.collection is None:
            self.initialize()
        return self.collection.count()
    
    def reset(self):
        """Reset collection (delete all documents)"""
        if self.client is None:
            self.initialize()
        
        logger.warning("Resetting vector store...")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "FPL expert articles for RAG"}
        )
        logger.info("✅ Vector store reset")


# Global vector store instance
_vector_store_instance = None


def get_vector_store() -> VectorStore:
    """Get global vector store instance (singleton pattern)"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
