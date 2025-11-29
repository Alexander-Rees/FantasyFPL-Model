"""
Groq test with error handling
"""
import sys
import traceback

print("Starting Groq test...", flush=True)

try:
    from groq import Groq
    print("✅ Groq imported", flush=True)
    
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    api_key = os.getenv("LLM_API_KEY")
    print(f"✅ Loaded API key: {api_key[:10]}...", flush=True)
    
    client = Groq(api_key=api_key)
    print("✅ Client created", flush=True)
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say 'Hello from Groq!' in one sentence."}],
        temperature=0.7,
        max_tokens=50
    )
    print("✅ API call completed", flush=True)
    
    result = completion.choices[0].message.content
    print(f"\n🎯 RESULT: {result}", flush=True)
    print("\n✅ SUCCESS!", flush=True)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}", flush=True)
    print(f"\nTraceback:", flush=True)
    traceback.print_exc()
    sys.exit(1)
