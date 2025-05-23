#!/usr/bin/env python3
"""
Test script for CoresAI Streaming Backend
Demonstrates different output modes and schema types
"""

import requests
import json
import time

def test_traditional_chat():
    """Test traditional chat endpoint"""
    print("🔄 Testing Traditional Chat Endpoint...")
    
    response = requests.post("http://localhost:8081/api/v1/chat", json={
        "messages": [{"role": "user", "content": "search for AI developments"}]
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Traditional chat working!")
        print(f"Response: {data['messages'][-1]['content'][:100]}...")
    else:
        print(f"❌ Error: {response.status_code}")

def test_schema_detection():
    """Test schema detection endpoint"""
    print("\n🔄 Testing Schema Detection...")
    
    test_messages = [
        "search for latest AI developments",
        "create notifications for team meeting", 
        "plan tasks for website redesign",
        "analyze market trends in technology",
        "hello there"
    ]
    
    for message in test_messages:
        response = requests.post("http://localhost:8081/api/v1/detect-schema", json={
            "message": message
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ '{message}' -> detected: {data['detected_schema']}")
        else:
            print(f"❌ Error detecting schema for: {message}")

def test_streaming_response():
    """Test streaming endpoint with different modes"""
    print("\n🔄 Testing Streaming Responses...")
    
    test_cases = [
        {
            "messages": [{"role": "user", "content": "search for AI developments"}],
            "output_mode": "object",
            "schema_type": "search",
            "description": "Search Results (Object Mode)"
        },
        {
            "messages": [{"role": "user", "content": "create notifications for team meeting"}],
            "output_mode": "array", 
            "schema_type": "notifications",
            "description": "Notifications (Array Mode)"
        },
        {
            "messages": [{"role": "user", "content": "analyze AI trends"}],
            "output_mode": "object",
            "schema_type": "analysis", 
            "description": "Analysis (Object Mode)"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['description']} ---")
        
        try:
            response = requests.post(
                "http://localhost:8081/api/v1/stream-object",
                json=test_case,
                stream=True,
                headers={'Accept': 'text/event-stream'}
            )
            
            if response.status_code == 200:
                print("✅ Streaming response:")
                chunk_count = 0
                
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])
                                chunk_count += 1
                                print(f"  Chunk {chunk_count}: {data['chunk_type']} (index: {data['chunk_index']})")
                                
                                if data.get('is_final'):
                                    print(f"  ✅ Completed with {chunk_count} chunks")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_health_check():
    """Test health endpoint"""
    print("\n🔄 Testing Health Check...")
    
    try:
        response = requests.get("http://localhost:8081/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Health: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Features: {', '.join(data['features'])}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")

def main():
    """Run all tests"""
    print("🚀 CoresAI Streaming Backend Test Suite")
    print("=" * 50)
    
    # Test health first
    test_health_check()
    
    # Test schema detection
    test_schema_detection()
    
    # Test traditional chat
    test_traditional_chat()
    
    # Test streaming
    test_streaming_response()
    
    print("\n" + "=" * 50)
    print("🎉 Testing complete! Check the streaming interface at:")
    print("   streaming_ai_interface.html")
    print("\n💡 To start the backend:")
    print("   python streaming_ai_backend.py")

if __name__ == "__main__":
    main() 