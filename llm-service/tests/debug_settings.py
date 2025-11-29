"""Debug settings loading"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

print("Settings loaded:")
print(f"LLM_API_PROVIDER: '{settings.LLM_API_PROVIDER}'")
print(f"LLM_API_KEY: '{settings.LLM_API_KEY[:20]}...' (truncated)")
print(f"LLM_API_MODEL: '{settings.LLM_API_MODEL}'")
