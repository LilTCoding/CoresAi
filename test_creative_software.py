import requests
import json

def test_creative_software_detection():
    """Test schema detection for creative software queries"""
    print("🧪 Testing Creative Software Schema Detection...")
    
    queries = [
        "How do I use the brush tool in Photoshop?",
        "Explain Blender's modeling workspace",
        "What is chroma key in VEGAS Pro?",
        "Tell me about 3D rendering",
        "How do layers work in graphics editing?"
    ]
    
    for query in queries:
        try:
            response = requests.post('http://localhost:8081/api/v1/detect-schema', 
                                   json={"message": query})
            result = response.json()
            print(f"Query: '{query}'")
            print(f"Detected Schema: {result['detected_schema']}")
            print("---")
        except Exception as e:
            print(f"Error testing detection: {e}")

def test_creative_software_response():
    """Test creative software knowledge generation"""
    print("\n🎨 Testing Creative Software Knowledge Generation...")
    
    try:
        # Test Photoshop query
        response = requests.post('http://localhost:8081/api/v1/chat', 
                               json={
                                   "messages": [
                                       {"role": "user", "content": "Tell me about Photoshop tools"}
                                   ]
                               })
        result = response.json()
        print("Photoshop Query Response:")
        print(result['messages'][-1]['content'][:200] + "...")
        print("---")
        
        # Test Blender query
        response = requests.post('http://localhost:8081/api/v1/chat', 
                               json={
                                   "messages": [
                                       {"role": "user", "content": "Explain Blender workspaces"}
                                   ]
                               })
        result = response.json()
        print("Blender Query Response:")
        print(result['messages'][-1]['content'][:200] + "...")
        print("---")
        
    except Exception as e:
        print(f"Error testing creative software response: {e}")

def test_backend_health():
    """Test backend health and features"""
    print("\n❤️ Testing Backend Health...")
    
    try:
        response = requests.get('http://localhost:8081/health')
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Version: {result['version']}")
        print(f"Features: {', '.join(result['features'])}")
        print(f"Message: {result['message']}")
        
        # Check if creative_software is in features
        if 'creative_software' in result['features']:
            print("✅ Creative Software Knowledge feature is enabled!")
        else:
            print("❌ Creative Software Knowledge feature not found in features list")
            
    except Exception as e:
        print(f"Error testing backend health: {e}")

def main():
    print("🚀 CoresAI Creative Software Knowledge Testing Suite")
    print("=" * 60)
    
    test_backend_health()
    test_creative_software_detection()
    test_creative_software_response()
    
    print("\n✨ Testing Complete!")

if __name__ == "__main__":
    main() 