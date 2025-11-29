"""
Test RAG System - Ingest articles and test queries
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.ingestion import ingest_scraped_articles
from app.models.vector_store import get_vector_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Ingest all scraped articles"""
    print("=" * 60)
    print("FPL RAG System - Article Ingestion")
    print("=" * 60)
    print()
    
    # Check if articles exist
    from app.core.config import settings
    scraped_path = Path(settings.SCRAPED_DATA_PATH)
    
    if not scraped_path.exists():
        print(f"❌ Scraped data path not found: {scraped_path}")
        print("\nPlease run the scraper first:")
        print("  cd scraper")
        print("  python weekly_scraper.py")
        return
    
    # Count markdown files
    md_files = list(scraped_path.rglob("*.md"))
    print(f"📁 Found {len(md_files)} markdown files")
    print()
    
    # Ingest articles
    print("🔄 Starting ingestion (this will download bge-m3 model ~2GB on first run)...")
    print()
    
    num_docs = ingest_scraped_articles(reset=True)
    
    print()
    print("=" * 60)
    print(f"✅ Ingestion complete!")
    print(f"📊 Total document chunks: {num_docs}")
    print()
    
    # Show vector store stats
    vector_store = get_vector_store()
    count = vector_store.get_count()
    print(f"💾 Vector store contains {count} documents")
    print()
    
    print("Next step: Test RAG queries")
    print("  python tests/test_rag_query.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
