# FPL LLM Service

AI-powered FPL insights using RAG + Llama 3.1 8B (MLX optimized for M1 Max)

## Features

- 🤖 **Llama 3.1 8B Instruct** via MLX (Apple Silicon optimized)
- 🔍 **RAG** with bge-m3 embeddings + Chroma vector store
- ⚡ **FastAPI** async service
- 🎯 **FPL-specific** insights (captaincy, transfers, player analysis)

## Quick Start

### 1. Install Dependencies

```bash
cd llm-service
pip install -r requirements.txt
```

**Note**: First run will download models (~6.5GB total):
- Llama 3.1 8B (4-bit): ~4.5GB
- bge-m3 embeddings: ~2GB

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 3. Run Service

```bash
# Development mode
python -m uvicorn app.main:app --reload --port 5002

# Or
cd app
python main.py
```

### 4. Test

```bash
# Health check
curl http://localhost:5002/health

# Service info
curl http://localhost:5002/api/v1/info
```

## API Endpoints

### Health & Info
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/info` - Service information

### Coming Soon (Phase 3)
- `POST /api/v1/insights/captaincy` - Captain recommendations
- `POST /api/v1/insights/transfers` - Transfer suggestions
- `POST /api/v1/insights/player/{id}` - Player analysis

## Architecture

```
llm-service/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   └── config.py        # Settings
│   ├── models/
│   │   ├── llm.py           # MLX Llama 3.1 8B
│   │   └── embeddings.py    # bge-m3 embeddings
│   └── api/                 # API endpoints (Phase 3)
├── data/
│   └── vector_db/           # Chroma database
├── scraper/                 # FPL content scraper
└── tests/                   # Unit tests
```

## Models

### LLM: Llama 3.1 8B Instruct
- **Framework**: MLX (Apple Silicon optimized)
- **Quantization**: 4-bit (efficient inference on M1 Max)
- **Model**: `mlx-community/Meta-Llama-3.1-8B-Instruct-4bit`
- **Speed**: ~2-5 seconds per response on M1 Max

### Embeddings: bge-m3
- **Model**: `BAAI/bge-m3`
- **Dimensions**: 1024
- **Use**: Semantic search for RAG

### Vector Store: Chroma
- **Type**: Embedded (no separate server)
- **Storage**: Local SQLite + embeddings

## Development

### Run Tests
```bash
pytest tests/
```

### Check Logs
```bash
tail -f logs/llm-service.log
```

## Next Steps

- [x] Phase 2: LLM service foundation
- [ ] Phase 3: RAG implementation
- [ ] Phase 4: Backend integration
- [ ] Phase 5: Frontend UI
