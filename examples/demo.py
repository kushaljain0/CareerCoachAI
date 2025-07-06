#!/usr/bin/env python3
"""
Career Coach AI Demo Script
Tests the MCP server endpoints and demonstrates the ReAct pattern.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            print(f"   LLM Available: {data['llm_available']}")
            print(f"   Providers: {data['llm_providers']}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")

def test_resume_analysis():
    """Test the resume analysis tool."""
    print("\n📄 Testing Resume Analysis...")
    
    sample_resume = """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    SUMMARY
    Experienced software engineer with 3 years developing web applications.
    
    EXPERIENCE
    Software Engineer, Tech Corp (2021-2024)
    - Developed React applications for client projects
    - Collaborated with team of 5 developers
    - Implemented new features and bug fixes
    
    SKILLS
    JavaScript, React, Python, SQL, Git
    """
    
    payload = {
        "resume_text": sample_resume,
        "use_llm": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tools/analyze_resume", 
                               json=payload, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resume Analysis: {data['analysis_type']}")
            print(f"   Resume Length: {data['resume_length']} characters")
            print(f"   Feedback: {data['feedback'][:200]}...")
        else:
            print(f"❌ Resume Analysis Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Resume Analysis Error: {e}")

def test_mock_interview():
    """Test the mock interview tool."""
    print("\n🎤 Testing Mock Interview...")
    
    payload = {
        "position": "data scientist",
        "use_llm": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/tools/mock_interview", 
                               json=payload, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mock Interview: {data['generation_type']}")
            print(f"   Position: {data['position']}")
            print(f"   Questions Generated: {len(data['questions'].split('\\n')) if isinstance(data['questions'], str) else len(data['questions'])}")
            if isinstance(data['questions'], list):
                print(f"   Sample Question: {data['questions'][0]}")
        else:
            print(f"❌ Mock Interview Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Mock Interview Error: {e}")

def test_career_guides():
    """Test the career guides resource."""
    print("\n📚 Testing Career Guides...")
    
    payload = {
        "query": "salary negotiation tips",
        "top_k": 3,
        "use_llm": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/resources/career_guides/featured", 
                               json=payload, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Career Guides: {data['generation_type']}")
            print(f"   Query: {data['query']}")
            print(f"   Sources: {data['sources']}")
            print(f"   Response Length: {len(str(data['tips']))} characters")
        else:
            print(f"❌ Career Guides Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Career Guides Error: {e}")

def test_chat_endpoint():
    """Test the main chat endpoint with ReAct pattern."""
    print("\n💬 Testing Chat Endpoint (ReAct Pattern)...")
    
    test_queries = [
        "Can you help me analyze my resume?",
        "I have an interview for a product manager position",
        "How do I transition from marketing to data science?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        payload = {
            "message": query,
            "use_rag": True,
            "use_tools": True
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat", 
                                   json=payload, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Response: {data['reasoning']}")
                if 'suggested_action' in data:
                    print(f"   🎯 Suggested Action: {data['suggested_action']}")
                if 'sources' in data:
                    print(f"   📖 Sources: {data['sources']}")
            else:
                print(f"   ❌ Chat Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Chat Error: {e}")
        
        time.sleep(1)  # Brief pause between requests

def test_server_info():
    """Test the root endpoint for server information."""
    print("\nℹ️  Testing Server Information...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server: {data['service']} v{data['version']}")
            print(f"   Tools: {len(data['tools'])}")
            print(f"   Resources: {len(data['resources'])}")
            print(f"   LLM Status: {data['llm_status']['default_llm']}")
        else:
            print(f"❌ Server Info Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Server Info Error: {e}")

def main():
    """Run all demo tests."""
    print("🚀 Career Coach AI Demo")
    print("=" * 50)
    
    # Test all endpoints
    test_health_check()
    test_server_info()
    test_resume_analysis()
    test_mock_interview()
    test_career_guides()
    test_chat_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\nTo use the system:")
    print("1. Frontend: http://localhost:3000")
    print("2. API Docs: http://localhost:8000/docs")
    print("3. Health Check: http://localhost:8000/health")

if __name__ == "__main__":
    main() 