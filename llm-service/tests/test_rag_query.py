"""
Test RAG Query - Ask FPL questions and get AI answers
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.rag import get_rag_pipeline
from app.models.vector_store import get_vector_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_retrieval_only():
    """Test vector store retrieval without LLM"""
    print("\n" + "=" * 60)
    print("Test 1: Vector Store Retrieval (No LLM)")
    print("=" * 60)
    
    vector_store = get_vector_store()
    vector_store.initialize()
    
    query = "Who should I captain this gameweek?"
    print(f"\n🔍 Query: {query}")
    print()
    
    results = vector_store.query(query, n_results=3)
    
    print(f"📚 Found {len(results['ids'][0])} relevant chunks:")
    print()
    
    for i in range(len(results['ids'][0])):
        metadata = results['metadatas'][0][i]
        text = results['documents'][0][i]
        distance = results['distances'][0][i]
        
        print(f"Result {i+1}:")
        print(f"  Title: {metadata['title']}")
        print(f"  GW: {metadata['gameweek']} | Category: {metadata['category']}")
        print(f"  Relevance: {1 - distance:.2%}")
        print(f"  Text: {text[:200]}...")
        print()


def test_rag_query(query: str, category: str = None):
    """Test full RAG pipeline with LLM"""
    print("\n" + "=" * 60)
    print("Test 2: Full RAG Pipeline (Retrieval + LLM)")
    print("=" * 60)
    
    print(f"\n🤖 Query: {query}")
    if category:
        print(f"📂 Category filter: {category}")
    print()
    
    print("⏳ Generating answer (this will download Llama 3.1 8B ~4.5GB on first run)...")
    print("   This may take 2-5 seconds on M1 Max...")
    print()
    
    rag = get_rag_pipeline()
    
    result = rag.answer_question(
        query=query,
        category=category,
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


def interactive_mode():
    """Interactive RAG query mode"""
    print("\n" + "=" * 60)
    print("Interactive RAG Query Mode")
    print("=" * 60)
    print()
    print("Ask FPL questions and get AI-powered answers!")
    print("Type 'quit' to exit")
    print()
    
    rag = get_rag_pipeline()
    
    while True:
        query = input("\n🤔 Your question: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        print("\n⏳ Thinking...")
        
        try:
            result = rag.answer_question(query, include_sources=True)
            
            print("\n" + "=" * 60)
            print("🎯 ANSWER:")
            print("=" * 60)
            print(result['answer'])
            print()
            
            if result.get('sources'):
                print("📚 Sources: " + ", ".join([
                    f"{s['title']} (GW{s['gameweek']})"
                    for s in result['sources'][:3]
                ]))
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print("\n👋 Goodbye!")


def main():
    """Run RAG tests"""
    print("=" * 60)
    print("FPL RAG System - Query Tests")
    print("=" * 60)
    
    # Check vector store has documents
    vector_store = get_vector_store()
    vector_store.initialize()
    count = vector_store.get_count()
    
    print(f"\n💾 Vector store contains {count} documents")
    
    if count == 0:
        print("\n❌ No documents in vector store!")
        print("\nPlease run ingestion first:")
        print("  python tests/test_ingestion.py")
        return
    
    print("\nChoose test mode:")
    print("1. Test retrieval only (fast, no LLM)")
    print("2. Test full RAG with sample question")
    print("3. Interactive mode (ask your own questions)")
    print("4. Run all tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        test_retrieval_only()
    
    elif choice == '2':
        test_rag_query(
            "Who should I captain this gameweek?",
            category="captaincy"
        )
    
    elif choice == '3':
        interactive_mode()
    
    elif choice == '4':
        test_retrieval_only()
        test_rag_query(
            "Who should I captain this gameweek?",
            category="captaincy"
        )
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
