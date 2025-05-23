import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CoresAI Simple Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    messages: List[Message]

class SimpleAI:
    """Simple AI responder for testing"""
    
    def generate_response(self, messages: List[Message]) -> str:
        # Get the last user message
        user_message = messages[-1].content if messages else "Hello"
        
        # Simple response logic based on keywords
        user_message_lower = user_message.lower()
        
        if "hello" in user_message_lower or "hi" in user_message_lower:
            return "Hello! I'm CoresAI, your advanced AI assistant. How can I help you today?"
        elif "help" in user_message_lower:
            return "I can help you with various tasks including answering questions, providing information, and having conversations. What would you like assistance with?"
        elif "name" in user_message_lower:
            return "I'm CoresAI, an advanced AI assistant designed to help with various tasks and provide intelligent responses."
        elif "weather" in user_message_lower:
            return "I don't have access to real-time weather data, but I'd be happy to help you find weather information or discuss weather-related topics!"
        elif "time" in user_message_lower:
            return "I don't have access to real-time clock data, but you can check the time on your device. Is there anything else I can help you with?"
        elif "goodbye" in user_message_lower or "bye" in user_message_lower:
            return "Goodbye! It was nice chatting with you. Feel free to come back anytime if you need assistance!"
        elif "?" in user_message:
            return f"That's an interesting question about '{user_message}'. While I'm still learning and developing my capabilities, I'd be happy to discuss this topic with you and share what I know."
        else:
            return f"I understand you're saying: '{user_message}'. That's interesting! I'm here to help and learn. Could you tell me more about what you'd like to discuss or how I can assist you?"

# Initialize the AI
ai = SimpleAI()

@app.get("/")
async def root():
    return {"message": "CoresAI Simple Backend is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Backend is running"}

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    try:
        # Generate AI response
        response_text = ai.generate_response(request.messages)
        
        # Create response message
        response_message = Message(role="assistant", content=response_text)
        
        # Return updated conversation
        updated_messages = request.messages + [response_message]
        
        return ChatResponse(messages=updated_messages)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/api/v1/server-status")
async def server_status(request: dict):
    return {"status": "running", "message": "Server is operational"}

if __name__ == "__main__":
    print("Starting CoresAI Simple Backend...")
    print("Server will be available at: http://localhost:8080")
    print("API documentation at: http://localhost:8080/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8080) 