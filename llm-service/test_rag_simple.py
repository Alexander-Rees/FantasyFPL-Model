#!/usr/bin/env python3
"""
Simple RAG test - ingest and query
"""
import sys
import os

# Set up path
sys.path.insert(0, '/Users/arees/fantasy-soccer-app/llm-service')
os.chdir('/Users/arees/fantasy-soccer-app/llm-service')

print("=" * 60)
print("FPL RAG System Test")
print("=" * 60)
print()

# Test 1: Check scraped articles
print("Step 1: Checking scraped articles...")
from pathlib import Path
scraped_path = Path('scraper/data/raw/scraped')
md_files = list(scraped_path.rglob("*.md"))
print(f"✅ Found {len(md_files)} markdown files")
print()

# Test 2: Initialize vector store
print("Step 2: Initializing vector store...")
from app.models.vector_store import get_vector_store
vector_store = get_vector_store()
vector_store.initialize()
print(f"✅ Vector store initialized ({vector_store.get_count()} documents)")
print()

# Test 3: Ingest articles (if empty)
if vector_store.get_count() == 0:
    print("Step 3: Ingesting articles (downloading bge-m3 ~2GB on first run)...")
    from app.core.ingestion import ingest_scraped_articles
    num_docs = ingest_scraped_articles(reset=False)
    print(f"✅ Ingested {num_docs} document chunks")
else:
    print(f"Step 3: Skipping ingestion (already have {vector_store.get_count()} documents)")
print()

# Test 4: Test retrieval
print("Step 4: Testing semantic search...")
query = "Who should I captain?"
results = vector_store.query(query, n_results=3)
print(f"Query: '{query}'")
print(f"✅ Found {len(results['ids'][0])} relevant chunks")
for i in range(min(2, len(results['ids'][0]))):
    meta = results['metadatas'][0][i]
    print(f"  - {meta['title']} (GW{meta['gameweek']}, {meta['category']})")
print()

print("=" * 60)
print("✅ RAG System Working!")
print("=" * 60)
print()
print("To test with LLM (downloads Llama 3.1 8B ~4.5GB):")
print("  python tests/test_rag_query.py")
