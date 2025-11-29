# Free LLM API Options for RAG

Yes! There are several **FREE** hosted Llama and open-source model APIs you can use!

## 🆓 Best Free Options

### 1. **Groq** ⭐ RECOMMENDED
**Completely FREE** with very fast inference!

- **Free Tier**: Unlimited requests (as of 2024)
- **Models**: Llama 3.1 8B, Llama 3.1 70B, Mixtral 8x7B
- **Speed**: Extremely fast (uses specialized hardware)
- **API Key**: Optional (can use without, but better with one)
- **Setup**: 
  ```bash
  pip install groq
  ```
  ```bash
  LLM_API_PROVIDER=groq
  LLM_API_KEY=  # Optional - can leave empty for free tier
  LLM_API_MODEL=llama-3.1-8b-instant  # or llama-3.1-70b-versatile
  ```

### 2. **Hugging Face Inference API**
**FREE tier** with generous limits!

- **Free Tier**: ~30,000 requests/month (varies)
- **Models**: All Hugging Face models including Llama, Mistral, etc.
- **API Key**: Optional for public models, required for private
- **Setup**:
  ```bash
  pip install requests
  ```
  ```bash
  LLM_API_PROVIDER=huggingface
  LLM_API_KEY=  # Optional for public models
  LLM_API_MODEL=meta-llama/Meta-Llama-3-8B-Instruct
  # or: mistralai/Mistral-7B-Instruct-v0.2
  ```

### 3. **Together AI**
**FREE tier** available!

- **Free Tier**: Limited but generous
- **Models**: Llama, Mistral, and more
- **Setup**: Similar to OpenAI format

## 🚀 Quick Setup with Groq (Recommended)

1. **Install package** (already in requirements-docker.txt):
   ```bash
   pip install groq
   ```

2. **Add to .env**:
   ```bash
   LLM_API_PROVIDER=groq
   LLM_API_KEY=  # Can leave empty or get free key from groq.com
   LLM_API_MODEL=llama-3.1-8b-instant
   ```

3. **Restart service**:
   ```bash
   docker compose -f infra/docker-compose.yml restart llm-service
   ```

4. **Test it** - You'll get fast, free AI-generated answers!

## 📊 Comparison

| Service | Free Tier | Speed | Models | Best For |
|---------|-----------|-------|--------|----------|
| **Groq** | ✅ Unlimited | ⚡⚡⚡ Very Fast | Llama 3.1, Mixtral | **Best choice!** |
| **Hugging Face** | ✅ ~30k/month | ⚡⚡ Fast | All HF models | Variety |
| **Together AI** | ✅ Limited | ⚡⚡ Fast | Llama, Mistral | Alternative |
| OpenAI | ❌ Pay-per-use | ⚡⚡⚡ Fast | GPT-4, GPT-3.5 | Quality |
| Anthropic | ❌ Pay-per-use | ⚡⚡⚡ Fast | Claude 3.5 | Quality |

## 💡 Recommendation

**Start with Groq** - it's completely free, extremely fast, and has great Llama models perfect for RAG!

## 🔧 Supported Models

### Groq:
- `llama-3.1-8b-instant` - Fast, good quality
- `llama-3.1-70b-versatile` - Better quality, still fast
- `mixtral-8x7b-32768` - Excellent for long context

### Hugging Face:
- `meta-llama/Meta-Llama-3-8B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.2`
- `google/gemma-7b-it`
- Many more!

## ⚠️ Notes

- **Groq**: Free tier may have rate limits, but very generous
- **Hugging Face**: Free tier has monthly limits, but usually enough for personal use
- **API Keys**: Some services work without keys, but having one gives better rate limits

## 🎯 Next Steps

1. Try Groq first (easiest, fastest, free)
2. If you hit limits, try Hugging Face
3. For production, consider paid APIs for reliability

