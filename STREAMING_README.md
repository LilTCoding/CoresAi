# CoresAI Structured Streaming

## Overview

CoresAI now supports structured object streaming similar to the Vercel AI SDK's `streamObject` functionality. This enables real-time generation of structured responses with different output modes and schema types.

## 🚀 Quick Start

### 1. Start the Streaming Backend

```bash
python streaming_ai_backend.py
```

The backend will start on `http://localhost:8080` with the following features:
- ✅ Structured streaming with multiple output modes
- ✅ Automatic schema detection 
- ✅ Real-time response generation
- ✅ Backward compatibility with existing endpoints

### 2. Open the Streaming Interface

Open `streaming_ai_interface.html` in your browser to access the advanced streaming interface with:
- 🎛️ Output mode controls (Object, Array, No-Schema)
- 🔍 Schema type selection (Auto-detect, Search, Notifications, Tasks, Analysis)
- 📊 Real-time streaming visualization
- 🛑 Stop streaming functionality

### 3. Test the API

Run the test suite to verify everything is working:

```bash
python test_streaming.py
```

## 📋 Schema Types

### 1. Search Results (`search`)
Perfect for web search queries and information retrieval.

**Example Request:**
```json
{
  "messages": [{"role": "user", "content": "search for AI developments"}],
  "output_mode": "object",
  "schema_type": "search"
}
```

**Response Structure:**
```json
{
  "query": "AI developments",
  "results": [
    {
      "title": "Latest AI Research",
      "snippet": "Recent advances in AI...",
      "url": "https://example.com",
      "relevance_score": 0.95
    }
  ],
  "summary": "Based on current research..."
}
```

### 2. Notifications (`notifications`)
Generate structured notification items.

**Example Request:**
```json
{
  "messages": [{"role": "user", "content": "create notifications for team meeting"}],
  "output_mode": "array",
  "schema_type": "notifications"
}
```

**Response Structure (Array Mode):**
```json
{
  "name": "Alice Johnson",
  "message": "Team meeting scheduled for tomorrow",
  "timestamp": "2024-01-15 14:30:00",
  "priority": "high"
}
```

### 3. Tasks (`tasks`)
Generate actionable task items with metadata.

**Example Request:**
```json
{
  "messages": [{"role": "user", "content": "plan tasks for website redesign"}],
  "output_mode": "object",
  "schema_type": "tasks"
}
```

**Response Structure:**
```json
{
  "tasks": [
    {
      "title": "Design Homepage Layout",
      "description": "Create wireframes and mockups",
      "priority": "high",
      "estimated_time": "4 hours",
      "category": "Design"
    }
  ]
}
```

### 4. Analysis (`analysis`)
Comprehensive analysis with findings and recommendations.

**Example Request:**
```json
{
  "messages": [{"role": "user", "content": "analyze market trends in technology"}],
  "output_mode": "object", 
  "schema_type": "analysis"
}
```

**Response Structure:**
```json
{
  "topic": "Technology Market Trends",
  "summary": "Comprehensive analysis reveals...",
  "key_points": [
    {
      "category": "Technical",
      "finding": "Key insights reveal...",
      "confidence": 0.85,
      "implications": "This suggests..."
    }
  ],
  "recommendations": ["Prioritize AI integration", "Focus on mobile-first"],
  "confidence_level": 0.88
}
```

### 5. General (`general`)
Flexible responses for general queries.

## 🎛️ Output Modes

### Object Mode (`object`)
Streams a complete structured object progressively. The object is built up piece by piece, with each chunk containing more complete data.

**Use Case:** When you need a complete, structured response that builds up over time.

**Example:** Search results that appear one by one, building a complete search response.

### Array Mode (`array`) 
Streams array elements one at a time. Each chunk contains a single item from the array.

**Use Case:** When you need to display items as soon as they're available.

**Example:** Notifications or tasks that appear individually as they're generated.

### No Schema Mode (`no-schema`)
Generates free-form JSON without predefined structure. The AI determines the response format based on the prompt.

**Use Case:** When you need flexible, dynamic response structures.

**Example:** Creative responses or when the structure should be determined by context.

## 🔧 API Endpoints

### Main Streaming Endpoint
```
POST /api/v1/stream-object
```

**Request Body:**
```json
{
  "messages": [{"role": "user", "content": "your message"}],
  "output_mode": "object|array|no-schema",
  "schema_type": "search|notifications|tasks|analysis|general",
  "context": "optional context"
}
```

**Response:** Server-Sent Events (SSE) stream with chunks:
```json
{
  "chunk_type": "partial|complete",
  "data": { /* structured data */ },
  "chunk_index": 0,
  "is_final": false
}
```

### Schema Detection
```
POST /api/v1/detect-schema
```

**Request Body:**
```json
{
  "message": "search for AI developments"
}
```

**Response:**
```json
{
  "message": "search for AI developments",
  "detected_schema": "search",
  "available_schemas": ["general", "search", "notifications", "tasks", "analysis"]
}
```

### Traditional Chat (Backward Compatibility)
```
POST /api/v1/chat
```

Maintains compatibility with existing chat implementations.

## 🎨 Frontend Integration

### JavaScript Streaming Example

```javascript
async function streamResponse(message, outputMode = 'object', schemaType = 'auto') {
  const response = await fetch('/api/v1/stream-object', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: [{ role: 'user', content: message }],
      output_mode: outputMode,
      schema_type: schemaType
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        console.log('Received chunk:', data);
        
        // Update your UI with the streaming data
        updateUI(data);
        
        if (data.is_final) {
          console.log('Streaming complete');
          break;
        }
      }
    }
  }
}
```

### React/Next.js Integration

For React applications, you can adapt the Vercel AI SDK pattern:

```typescript
// hooks/useStreamObject.ts
import { useState, useCallback } from 'react';

interface StreamObjectOptions {
  api: string;
  outputMode: 'object' | 'array' | 'no-schema';
  schemaType: string;
}

export function useStreamObject(options: StreamObjectOptions) {
  const [object, setObject] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const submit = useCallback(async (message: string) => {
    setIsLoading(true);
    
    const response = await fetch(options.api, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [{ role: 'user', content: message }],
        output_mode: options.outputMode,
        schema_type: options.schemaType
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      // Parse and update object state
      // Implementation depends on your needs
    }

    setIsLoading(false);
  }, [options]);

  return { object, submit, isLoading };
}
```

## 🛠️ Advanced Features

### Auto Schema Detection
Set `schema_type: "auto"` to automatically detect the appropriate schema based on the user's message.

### Streaming Controls
- **Stop Streaming:** Close the connection at any time
- **Chunk Tracking:** Monitor chunk count and progress
- **Error Handling:** Graceful error recovery

### Confidence Scores
Analysis responses include confidence scores for findings and overall analysis.

### Progressive Loading
Object mode builds responses progressively, allowing for smooth loading animations.

## 🔄 Comparison with Vercel AI SDK

| Feature | Vercel AI SDK | CoresAI Streaming |
|---------|---------------|-------------------|
| Output Modes | ✅ Object, Array, No-Schema | ✅ Object, Array, No-Schema |
| Schema Definition | ✅ Zod schemas | ✅ Pydantic models |
| Streaming | ✅ Server-Sent Events | ✅ Server-Sent Events |
| Stop Function | ✅ Yes | ✅ Yes |
| Loading States | ✅ Yes | ✅ Yes |
| Auto Schema Detection | ❌ Manual | ✅ Automatic |
| Backend | ✅ Next.js | ✅ FastAPI |
| Type Safety | ✅ TypeScript | ✅ Python/Pydantic |

## 🚀 Production Deployment

### Environment Variables
```env
CORS_ORIGINS=https://yourdomain.com
API_PORT=8080
STREAMING_TIMEOUT=30
```

### Docker Setup
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "streaming_ai_backend.py"]
```

### Performance Considerations
- Use connection pooling for high traffic
- Implement rate limiting
- Monitor memory usage during streaming
- Set appropriate timeouts

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test all endpoints
python test_streaming.py

# Test specific schema types
python -c "
import requests
response = requests.post('http://localhost:8080/api/v1/detect-schema', 
                        json={'message': 'search for AI'})
print(response.json())
"
```

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the backend allows your frontend origin
2. **Connection Timeouts**: Check network connectivity and server status
3. **Schema Detection**: Verify message content matches expected patterns
4. **Memory Usage**: Monitor streaming for large responses

### Debug Mode
Enable debug logging in the backend:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Examples

Check out the included examples:
- `streaming_ai_interface.html` - Complete frontend implementation
- `test_streaming.py` - API testing examples
- `schemas.py` - Schema definitions

## 🎯 Next Steps

1. **Start the backend**: `python streaming_ai_backend.py`
2. **Open the interface**: `streaming_ai_interface.html`
3. **Try different modes**: Experiment with object, array, and no-schema modes
4. **Test schema types**: Try search, notifications, tasks, and analysis
5. **Integrate into your app**: Use the API patterns in your own application

## 🆘 Support

For issues or questions:
1. Check the test suite output
2. Verify backend health at `/health`
3. Review the streaming logs
4. Ensure all dependencies are installed

Happy streaming! 🚀 