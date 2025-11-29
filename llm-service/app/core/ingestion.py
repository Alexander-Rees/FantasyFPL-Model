"""
Document Ingestion - Load scraped articles into vector store
"""
from pathlib import Path
from app.models.vector_store import get_vector_store
from app.core.config import settings
import logging
import re
import hashlib
import uuid

logger = logging.getLogger(__name__)


def parse_markdown_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from markdown
    
    Args:
        content: Markdown content with frontmatter
        
    Returns:
        Tuple of (metadata dict, content without frontmatter)
    """
    metadata = {}
    
    # Check for frontmatter
    if not content.startswith('---'):
        return metadata, content
    
    # Split frontmatter and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        return metadata, content
    
    frontmatter = parts[1].strip()
    content_body = parts[2].strip()
    
    # Parse frontmatter (simple key: value parsing)
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    return metadata, content_body


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in words
        overlap: Overlap size in words
        
    Returns:
        List of text chunks
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP
    
    # Split into words
    words = text.split()
    
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


def ingest_scraped_articles(reset: bool = False) -> int:
    """
    Ingest all scraped articles into vector store
    
    Args:
        reset: Whether to reset vector store before ingesting
        
    Returns:
        Number of documents ingested
    """
    logger.info("Starting article ingestion...")
    
    # Get vector store
    vector_store = get_vector_store()
    vector_store.initialize()
    
    if reset:
        vector_store.reset()
    
    # Find all markdown files
    scraped_path = Path(settings.SCRAPED_DATA_PATH)
    if not scraped_path.exists():
        logger.error(f"Scraped data path not found: {scraped_path}")
        return 0
    
    markdown_files = list(scraped_path.rglob("*.md"))
    logger.info(f"Found {len(markdown_files)} markdown files")
    
    documents = []
    metadatas = []
    ids = []
    
    for md_file in markdown_files:
        try:
            # Read file
            content = md_file.read_text(encoding='utf-8')
            
            # Parse frontmatter
            metadata, body = parse_markdown_frontmatter(content)
            
            # Skip if too short
            if len(body) < 100:
                continue
            
            # Chunk the content
            chunks = chunk_text(body)
            
            for i, chunk in enumerate(chunks):
                # Generate unique IDs for each document to avoid duplicates
                chunk_id = str(uuid.uuid4())
                
                # Prepare metadata
                chunk_metadata = {
                    "source": metadata.get("source", "Unknown"),
                    "title": metadata.get("title", md_file.stem),
                    "category": metadata.get("category", "general"),
                    "gameweek": int(metadata.get("gameweek", 0)),
                    "url": metadata.get("url", ""),
                    "file_path": str(md_file.relative_to(scraped_path)),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                documents.append(chunk)
                metadatas.append(chunk_metadata)
                ids.append(chunk_id)
        
        except Exception as e:
            logger.warning(f"Failed to process {md_file}: {e}")
            continue
    
    # Add to vector store
    if documents:
        logger.info(f"Ingesting {len(documents)} document chunks...")
        vector_store.add_documents(documents, metadatas, ids)
        logger.info(f"✅ Ingestion complete! Total documents: {vector_store.get_count()}")
    else:
        logger.warning("No documents to ingest")
    
    return len(documents)


def ingest_gameweek_articles(gameweek: int) -> int:
    """
    Ingest articles for a specific gameweek
    
    Args:
        gameweek: Gameweek number
        
    Returns:
        Number of documents ingested
    """
    logger.info(f"Ingesting articles for GW{gameweek}...")
    
    # Get vector store
    vector_store = get_vector_store()
    vector_store.initialize()
    
    # Find gameweek directory
    scraped_path = Path(settings.SCRAPED_DATA_PATH)
    gw_path = scraped_path / f"gw{gameweek}"
    
    if not gw_path.exists():
        logger.error(f"Gameweek directory not found: {gw_path}")
        return 0
    
    markdown_files = list(gw_path.glob("*.md"))
    logger.info(f"Found {len(markdown_files)} files for GW{gameweek}")
    
    documents = []
    metadatas = []
    ids = []
    
    for md_file in markdown_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            metadata, body = parse_markdown_frontmatter(content)
            
            if len(body) < 100:
                continue
            
            chunks = chunk_text(body)
            
            for i, chunk in enumerate(chunks):
                chunk_id = hashlib.md5(
                    f"{md_file.stem}_{i}".encode()
                ).hexdigest()
                
                chunk_metadata = {
                    "source": metadata.get("source", "Unknown"),
                    "title": metadata.get("title", md_file.stem),
                    "category": metadata.get("category", "general"),
                    "gameweek": gameweek,
                    "url": metadata.get("url", ""),
                    "file_path": str(md_file.relative_to(scraped_path)),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                documents.append(chunk)
                metadatas.append(chunk_metadata)
                ids.append(chunk_id)
        
        except Exception as e:
            logger.warning(f"Failed to process {md_file}: {e}")
            continue
    
    if documents:
        vector_store.add_documents(documents, metadatas, ids)
        logger.info(f"✅ Ingested {len(documents)} chunks for GW{gameweek}")
    
    return len(documents)
