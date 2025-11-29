#!/usr/bin/env python3
"""Test LLM generation using retrieved context from vector store."""
import sys, os
sys.path.insert(0, '/Users/arees/fantasy-soccer-app/llm-service')

from app.models.llm import LLMModel
from app.models.vector_store import get_vector_store

vs = get_vector_store()
query = "Who should I captain this gameweek?"
results = vs.query(query, n_results=3)
contexts = []
for doc in results.get('documents', [[]])[0]:
    contexts.append(doc)

# Build prompt with proper formatting
prompt = (
    "You are a helpful FPL assistant. Using the following article excerpts, answer the question concisely.\n\n"
    "Context:\n" + "\n---\n".join(contexts) + "\n\n"
    f"Question: {query}\n"
    "Answer:"
)

llm = LLMModel()
answer = llm.generate(prompt)
print("Answer:", answer)
