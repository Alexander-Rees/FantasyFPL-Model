"""
Quick Groq API test
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.rag import get_rag_pipeline

print("Testing Groq API...")
print("=" * 60)

rag = get_rag_pipeline()
result = rag.answer_question("Who should I captain this gameweek?", include_sources=True)

print("\n🎯 ANSWER:")
print("=" * 60)
print(result['answer'])
print()

if result.get('sources'):
    print("📚 Sources:")
    for s in result['sources'][:3]:
        print(f"- {s['title']} (GW{s['gameweek']})")
