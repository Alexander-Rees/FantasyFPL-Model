#!/usr/bin/env python3
"""
Test RAG API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5002"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_info():
    """Test info endpoint"""
    print("=" * 60)
    print("Testing Info Endpoint")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/api/v1/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_retrieve():
    """Test retrieval endpoint (no LLM)"""
    print("=" * 60)
    print("Testing Retrieval Endpoint (No LLM)")
    print("=" * 60)
    query = "Who should I captain this gameweek?"
    print(f"Query: {query}")
    print()
    
    response = requests.get(
        f"{BASE_URL}/api/v1/retrieve",
        params={"query": query, "top_k": 3}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data['count']} results")
    print()
    
    for i, result in enumerate(data['results'], 1):
        print(f"Result {i}:")
        print(f"  Title: {result['metadata']['title']}")
        print(f"  GW: {result['metadata']['gameweek']} | Category: {result['metadata']['category']}")
        print(f"  Relevance: {result['relevance']:.2%}")
        print(f"  Text: {result['text'][:200]}...")
        print()
    print()

def test_rag_query():
    """Test full RAG query endpoint"""
    print("=" * 60)
    print("Testing RAG Query Endpoint (With LLM)")
    print("=" * 60)
    print("⚠️  This will download Llama 3.1 8B (~4.5GB) on first run")
    print("⚠️  This may take 2-5 seconds to generate response")
    print()
    
    query = "Who should I captain this gameweek?"
    print(f"Query: {query}")
    print()
    
    payload = {
        "query": query,
        "include_sources": True
    }
    
    print("⏳ Sending request...")
    response = requests.post(
        f"{BASE_URL}/api/v1/query",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print()
        print("=" * 60)
        print("ANSWER:")
        print("=" * 60)
        print(data['answer'])
        print()
        
        if data.get('sources'):
            print("=" * 60)
            print("SOURCES:")
            print("=" * 60)
            for i, source in enumerate(data['sources'], 1):
                print(f"{i}. {source['title']} (GW{source['gameweek']}, {source['category']})")
                print(f"   Relevance: {source['relevance']:.2%}")
            print()
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("=" * 60)
    print("FPL RAG API Tests")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_info()
        test_retrieve()
        
        print("Test full RAG with LLM? (y/n): ", end="")
        test_llm = input().strip().lower() == 'y'
        
        if test_llm:
            test_rag_query()
        else:
            print("\n⏭️  Skipping LLM test")
            print("   To test with LLM, run this script again and choose 'y'")
            print()
        
        print("=" * 60)
        print("✅ API Tests Complete!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to service")
        print("   Make sure the service is running:")
        print("   python -m uvicorn app.main:app --port 5002")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

