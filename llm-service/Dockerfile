# LLM Service Dockerfile
# Note: MLX is Apple Silicon only, so we use PyTorch/transformers in Docker
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# Use Docker-compatible requirements (no MLX)
COPY requirements-docker.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for vector store
RUN mkdir -p /app/data/vector_db

# Expose port
EXPOSE 5002

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002"]

