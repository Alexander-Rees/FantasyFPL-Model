# Testing the RAG System

## Quick Start Guide

### Step 1: Ingest Articles

First, load your scraped articles into the vector store:

```bash
cd llm-service
python tests/test_ingestion.py
```

**What happens:**
- Downloads bge-m3 embedding model (~2GB) on first run
- Chunks all scraped articles
- Generates embeddings
- Stores in Chroma vector database

**Expected output:**
```
📁 Found 18 markdown files
🔄 Starting ingestion...
✅ Ingestion complete!
📊 Total document chunks: 45
💾 Vector store contains 45 documents
```

### Step 2: Test RAG Queries

Test the system with FPL questions:

```bash
python tests/test_rag_query.py
```

**Test modes:**

1. **Retrieval Only** (fast, no LLM)
   - Tests semantic search
   - Shows relevant article chunks
   - No model download needed

2. **Full RAG** (downloads Llama 3.1 8B on first run)
   - Complete RAG pipeline
   - Downloads ~4.5GB model
   - Generates AI answers

3. **Interactive Mode**
   - Ask your own FPL questions
   - Get real-time AI answers
   - Perfect for testing

## Example Questions

Try these FPL questions:

**Captaincy:**
- "Who should I captain this gameweek?"
- "Is Haaland a good captain pick?"
- "Should I captain Salah or Son?"

**Transfers:**
- "Who are the best transfer targets?"
- "Should I transfer out Haaland?"
- "Which players should I bring in?"

**General:**
- "What are the best fixtures this gameweek?"
- "Who are good differential picks?"
- "Which defenders should I target?"

## Performance

On M1 Max:
- **Retrieval**: <1 second
- **LLM Generation**: 2-5 seconds
- **Total RAG query**: 3-6 seconds

## Troubleshooting

**No documents in vector store:**
```bash
# Run scraper first
cd scraper
python weekly_scraper.py

# Then ingest
cd ../llm-service
python tests/test_ingestion.py
```

**Model download slow:**
- First run downloads ~6.5GB total
- Cached for future use in `~/.cache/huggingface/`
- Ensure good internet connection

**Out of memory:**
- M1 Max 32GB should handle easily
- Close other apps if needed
- 4-bit quantized model is memory efficient
