# RAG System Testing Guide

## Current Status

✅ **RAG Pipeline**: Fully implemented  
✅ **Vector Store**: 46 documents ingested  
✅ **API Endpoints**: Working  
✅ **Retrieval**: Tested and working  
⏳ **LLM Generation**: Ready to test (requires model download)

## Quick Test

### 1. Test Retrieval Only (Fast, No LLM)

```bash
cd llm-service

# Via API
curl "http://localhost:5002/api/v1/retrieve?query=Who%20should%20I%20captain%20this%20gameweek?&top_k=3"

# Or use the test script
python test_api.py
# Choose 'n' when asked about LLM
```

### 2. Test Full RAG with LLM

**Note**: First run will download Llama 3.1 8B (~4.5GB) and may take 2-5 seconds per query.

```bash
# Via API
curl -X POST http://localhost:5002/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who should I captain this gameweek?",
    "include_sources": true
  }'

# Or use the test script
python test_api.py
# Choose 'y' when asked about LLM
```

### 3. Interactive Testing

```bash
# Interactive RAG query mode
python tests/test_rag_query.py
# Choose option 3 for interactive mode
```

## API Endpoints

### Health Check
```bash
GET http://localhost:5002/health
```

### Service Info
```bash
GET http://localhost:5002/api/v1/info
```

### Retrieval Only (No LLM)
```bash
GET http://localhost:5002/api/v1/retrieve?query=<your_query>&top_k=5
```

### Full RAG Query (With LLM)
```bash
POST http://localhost:5002/api/v1/query
Content-Type: application/json

{
  "query": "Who should I captain this gameweek?",
  "category": "captaincy",  # optional
  "gameweek": 12,           # optional
  "include_sources": true   # optional
}
```

## Complete Test Script

Run the complete test (ingestion + retrieval + optional LLM):

```bash
python test_rag_complete.py
```

## Starting the Service

```bash
cd llm-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 5002
```

Or:

```bash
cd llm-service/app
python main.py
```

## What's Working

1. ✅ **Vector Store**: Chroma DB with 46 document chunks
2. ✅ **Embeddings**: bge-m3 model (downloaded on first run)
3. ✅ **Retrieval**: Semantic search working correctly
4. ✅ **API Endpoints**: All endpoints functional
5. ✅ **RAG Pipeline**: Complete implementation ready

## Next Steps

1. **Test LLM Generation**: Run a full RAG query to download and test Llama 3.1 8B
2. **Add More Articles**: Run the scraper to get more FPL content
3. **Frontend Integration**: Connect the frontend to the RAG API
4. **Fine-tuning**: Adjust chunk size, top_k, and prompts based on results

## Troubleshooting

### Vector Store Empty
```bash
python tests/test_ingestion.py
```

### Service Not Starting
```bash
# Check if port 5002 is in use
lsof -ti:5002 | xargs kill -9

# Start service
python -m uvicorn app.main:app --port 5002
```

### LLM Not Working
- First run downloads ~4.5GB model
- Requires MLX (Apple Silicon optimized)
- Check logs for errors

