
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Checking imports...")
try:
    from llama_cpp import Llama
    print("✅ llama_cpp imported successfully")
except ImportError as e:
    print(f"❌ llama_cpp import failed: {e}")

from app.core.config import settings
print(f"Config LLM_MODEL_PATH: {settings.LLM_MODEL_PATH}")
print(f"Path exists: {os.path.exists(settings.LLM_MODEL_PATH)}")
print(f"CWD: {os.getcwd()}")

from app.models.llm import LLAMA_CPP_AVAILABLE
print(f"LLAMA_CPP_AVAILABLE in app.models.llm: {LLAMA_CPP_AVAILABLE}")
