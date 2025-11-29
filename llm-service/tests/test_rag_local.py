"""
Non-interactive RAG test for Local Llama
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.rag import get_rag_pipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("Testing Local Llama RAG (Non-Interactive)")
    print("=" * 60)
    
    query = "Who should I captain this gameweek?"
    print(f"\n🤖 Query: {query}")
    
    rag = get_rag_pipeline()
    
    # Force load model first to see logs
    print("\n⏳ Loading model...")
    rag.llm.load_model()
    
    if hasattr(rag.llm, 'use_llama_cpp') and rag.llm.use_llama_cpp:
        print("✅ Using llama-cpp-python (Local GGUF)")
    elif hasattr(rag.llm, 'use_mlx') and rag.llm.use_mlx:
        print("✅ Using MLX (Apple Silicon)")
    else:
        print("⚠️ Using Fallback/PyTorch")
        
    print("\n⏳ Generating answer...")
    result = rag.answer_question(query, include_sources=True)
    
    print("\n" + "=" * 60)
    print("🎯 ANSWER:")
    print("=" * 60)
    print(result['answer'])
    print()
    
    if result.get('sources'):
        print("📚 Sources:")
        for s in result['sources']:
            print(f"- {s['title']} (GW{s['gameweek']})")

if __name__ == "__main__":
    main()
