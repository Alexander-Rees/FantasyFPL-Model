"""
Simple Groq test - direct API call
"""
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

print("Testing Groq API...")
print("=" * 60)

completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {
            "role": "user",
            "content": "In one sentence, who should I captain in FPL this week?"
        }
    ],
    temperature=0.7,
    max_tokens=100,
    stream=False
)

print("\n🎯 ANSWER:")
print("=" * 60)
print(completion.choices[0].message.content)
print()
print("✅ Groq API working!")
