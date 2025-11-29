#!/usr/bin/env python3
"""
Complete RAG Test - Ingest articles and test queries
"""
import sys
import os
from pathlib import Path

# Set up path
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

print("=" * 60)
print("FPL RAG System - Complete Test")
print("=" * 60)
print()

# Step 1: Check scraped articles
print("Step 1: Checking scraped articles...")
from app.core.config import settings
scraped_path = Path(settings.SCRAPED_DATA_PATH)
md_files = list(scraped_path.rglob("*.md")) if scraped_path.exists() else []
print(f"✅ Found {len(md_files)} markdown files")
print()

# Step 2: Initialize and check vector store
print("Step 2: Checking vector store...")
from app.models.vector_store import get_vector_store
vector_store = get_vector_store()
vector_store.initialize()
count = vector_store.get_count()
print(f"📊 Vector store has {count} documents")
print()

# Step 3: Ingest articles if needed
if count == 0:
    print("Step 3: Ingesting articles (this will download bge-m3 ~2GB on first run)...")
    from app.core.ingestion import ingest_scraped_articles
    num_docs = ingest_scraped_articles(reset=False)
    print(f"✅ Ingested {num_docs} document chunks")
    count = vector_store.get_count()
    print(f"📊 Vector store now has {count} documents")
else:
    print(f"Step 3: Skipping ingestion (already have {count} documents)")
print()

# Step 4: Test retrieval only
print("Step 4: Testing semantic search (retrieval only)...")
query = "Who should I captain this gameweek?"
print(f"Query: '{query}'")
results = vector_store.query(query, n_results=3)
print(f"✅ Found {len(results['ids'][0])} relevant chunks")
for i in range(min(2, len(results['ids'][0]))):
    meta = results['metadatas'][0][i]
    text = results['documents'][0][i]
    print(f"  {i+1}. {meta['title']} (GW{meta['gameweek']}, {meta['category']})")
    print(f"     {text[:150]}...")
print()

# Step 5: Test full RAG (optional - requires LLM)
print("Step 5: Test full RAG with LLM?")
print("  (This will download Llama 3.1 8B ~4.5GB on first run)")
test_llm = input("  Test with LLM? (y/n): ").strip().lower() == 'y'

if test_llm:
    print("\n⏳ Testing full RAG pipeline...")
    print("   This may take 2-5 seconds on M1 Max...")
    print()
    
    from app.core.rag import get_rag_pipeline
    rag = get_rag_pipeline()
    
    result = rag.answer_question(
        query=query,
        include_sources=True
    )
    
    print("=" * 60)
    print("🎯 ANSWER:")
    print("=" * 60)
    print(result['answer'])
    print()
    
    if result.get('sources'):
        print("=" * 60)
        print("📚 SOURCES:")
        print("=" * 60)
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['title']} (GW{source['gameweek']}, {source['category']})")
            print(f"   Relevance: {source['relevance']:.2%}")
        print()
else:
    print("\n⏭️  Skipping LLM test")
    print("   To test with LLM later, run:")
    print("   python tests/test_rag_query.py")
    print()

print("=" * 60)
print("✅ RAG System Test Complete!")
print("=" * 60)
print()
print("Next steps:")
print("  1. Test via API: Start the service and use POST /api/v1/query")
print("  2. Interactive mode: python tests/test_rag_query.py (option 3)")
print("  3. Test retrieval: python tests/test_rag_query.py (option 1)")

