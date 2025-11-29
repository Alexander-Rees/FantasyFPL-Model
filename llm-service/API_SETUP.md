# LLM API Setup Guide

You can use external LLM API services (OpenAI, Anthropic) with the RAG system instead of running models locally.

## Supported Providers

1. **OpenAI** - GPT-4, GPT-4o, GPT-4o-mini, GPT-3.5-turbo
2. **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku

## Setup

### 1. Install API Client Packages

```bash
# For OpenAI
pip install openai

# For Anthropic
pip install anthropic

# Or both
pip install openai anthropic
```

### 2. Configure Environment Variables

Create or update `.env` file in `llm-service/`:

```bash
# Choose provider: 'openai' or 'anthropic'
LLM_API_PROVIDER=openai

# Your API key
LLM_API_KEY=sk-your-api-key-here

# Model to use
# OpenAI options: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
# Anthropic options: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307
LLM_API_MODEL=gpt-4o-mini
```

### 3. Restart Service

```bash
# If using Docker
docker compose -f infra/docker-compose.yml restart llm-service

# If running locally
python -m uvicorn app.main:app --port 5002
```

## Example Configurations

### OpenAI (Recommended for cost/performance)

```bash
LLM_API_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_API_MODEL=gpt-4o-mini  # Fast and cheap
# LLM_API_MODEL=gpt-4o  # More capable but expensive
```

### Anthropic (Best quality)

```bash
LLM_API_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_API_MODEL=claude-3-5-sonnet-20241022  # Best quality
# LLM_API_MODEL=claude-3-haiku-20240307  # Faster/cheaper
```

## How It Works

1. **Retrieval**: The system retrieves relevant FPL articles from the vector store
2. **Context Building**: Relevant excerpts are combined with your question
3. **API Call**: The LLM API generates an answer based on the context
4. **Response**: You get an AI-generated answer with source citations

## Benefits

- ✅ No need to download/run large models locally
- ✅ Works in Docker without model compatibility issues
- ✅ Faster responses (API services are optimized)
- ✅ Access to latest models (GPT-4, Claude 3.5)
- ✅ Pay-per-use pricing (cost-effective for low volume)

## Cost Estimates

### OpenAI
- GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- GPT-4o: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens
- Typical query: ~$0.001-0.01 per question

### Anthropic
- Claude 3.5 Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Claude 3 Haiku: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- Typical query: ~$0.01-0.05 per question

## Testing

Test the API setup:

```bash
curl -X POST http://localhost:5002/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who should I captain this gameweek?",
    "include_sources": true
  }'
```

You should get a full AI-generated answer instead of the retrieval-only fallback.

## Troubleshooting

### "LLM_API_KEY must be set"
- Make sure you've set `LLM_API_KEY` in your `.env` file
- Check that the `.env` file is in the `llm-service/` directory

### "Unsupported provider"
- Make sure `LLM_API_PROVIDER` is set to 'openai' or 'anthropic'
- Check spelling (case-insensitive)

### "API generation failed"
- Verify your API key is valid
- Check your API account has credits/quota
- Review service logs: `docker compose -f infra/docker-compose.yml logs llm-service`

### Still getting retrieval-only responses
- Check logs to see if API calls are being made
- Verify the API client is initialized: Look for "Initialized OpenAI/Anthropic client" in logs

