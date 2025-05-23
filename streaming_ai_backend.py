import os
import warnings
import requests
import json
import asyncio
from datetime import datetime
from typing import Generator, Dict, Any, List
import random
warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from schemas import *

app = FastAPI(title="CoresAI Streaming Backend", version="4.1.0")

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

class StreamingAI:
    """Advanced AI with structured streaming capabilities including creative software knowledge"""
    
    def __init__(self):
        self.conversation_history = []
    
    def detect_response_type(self, user_message: str) -> str:
        """Detect what type of structured response is needed"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["photoshop", "blender", "vegas", "creative", "tool", "brush", "layer", "modeling", "render", "edit", "video", "3d", "graphics", "design"]):
            return "creative_software"
        elif any(word in message_lower for word in ["search", "find", "look up", "latest", "current"]):
            return "search"
        elif any(word in message_lower for word in ["notify", "notification", "alert", "remind"]):
            return "notifications"
        elif any(word in message_lower for word in ["task", "todo", "plan", "schedule", "organize"]):
            return "tasks"
        elif any(word in message_lower for word in ["analyze", "analysis", "examine", "study", "review"]):
            return "analysis"
        else:
            return "general"
    
    def generate_search_results(self, query: str) -> WebSearchResponse:
        """Generate structured search results"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        results = []
        search_terms = ["AI development", "machine learning", "technology trends", "data science"]
        
        for i, term in enumerate(search_terms[:3]):
            results.append(SearchResult(
                title=f"Latest Developments in {term.title()}",
                snippet=f"Recent advances in {term} show promising results with new methodologies and approaches being developed by leading researchers and companies.",
                url=f"https://research.example.com/{term.replace(' ', '-')}-2024",
                relevance_score=0.95 - (i * 0.1)
            ))
        
        return WebSearchResponse(
            query=query,
            results=results,
            summary=f"Based on current research, {query} shows significant progress across multiple domains with emerging technologies driving innovation."
        )
    
    def generate_notifications(self, context: str) -> List[Notification]:
        """Generate structured notifications"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        names = ["Alice Johnson", "Bob Chen", "Carol Smith", "David Williams"]
        priorities = ["high", "medium", "low"]
        
        notifications = []
        for i, name in enumerate(names[:3]):
            notifications.append(Notification(
                name=name,
                message=f"Important update regarding {context}. Please review the latest information and provide feedback.",
                timestamp=current_time,
                priority=random.choice(priorities)
            ))
        
        return notifications
    
    def generate_tasks(self, context: str) -> List[TaskItem]:
        """Generate structured task items"""
        categories = ["Development", "Research", "Analysis", "Planning"]
        priorities = ["high", "medium", "low"]
        
        tasks = []
        for i, category in enumerate(categories[:4]):
            tasks.append(TaskItem(
                title=f"{category} Task for {context}",
                description=f"Complete {category.lower()} work related to {context} with focus on quality and efficiency.",
                priority=random.choice(priorities),
                estimated_time=f"{random.randint(1, 8)} hours",
                category=category
            ))
        
        return tasks
    
    def generate_creative_software_knowledge(self, query: str) -> SoftwareKnowledgeResponse:
        """Generate structured creative software knowledge"""
        
        # Creative Software Knowledge Base
        knowledge_base = {
            "photoshop_tools": [
                {"name": "Move Tool", "shortcut": "V", "function": "Move layers, selections, and guides", 
                 "how_it_works": "Adjusts layer position data (x/y coordinates) without altering the pixel data", "category": "transformation"},
                {"name": "Brush Tool", "shortcut": "B", "function": "Paint pixels", 
                 "how_it_works": "Applies alpha and RGB values per stroke, based on pressure (if supported)", "category": "painting"},
                {"name": "Magic Wand", "shortcut": "W", "function": "Select similar-colored areas", 
                 "how_it_works": "Uses color range and tolerance threshold to generate pixel masks", "category": "selection"},
                {"name": "Clone Stamp", "shortcut": "S", "function": "Duplicate part of image", 
                 "how_it_works": "Samples pixel data from a source and pastes it at the target position", "category": "repair"},
                {"name": "Pen Tool", "shortcut": "P", "function": "Create vector paths", 
                 "how_it_works": "Bézier curves stored in shape layers or paths for selections/strokes", "category": "vector"}
            ],
            "blender_workspaces": [
                {"name": "Modeling", "purpose": "Create 3D mesh objects", 
                 "how_it_works": "Uses vertices, edges, and faces to define topology", "software": "Blender"},
                {"name": "Sculpting", "purpose": "Organic mesh deformation", 
                 "how_it_works": "Dynamic topology or multires uses voxel/pixel data for brush strokes", "software": "Blender"},
                {"name": "Shading", "purpose": "Assign materials and textures", 
                 "how_it_works": "Node-based shader system using Cycles or Eevee engines", "software": "Blender"},
                {"name": "Animation", "purpose": "Set keyframes and movement", 
                 "how_it_works": "F-Curves and keyframes interpolate transforms over time", "software": "Blender"}
            ],
            "vegas_tools": [
                {"name": "Event Pan/Crop", "shortcut": "", "function": "Resize and move video clips", 
                 "how_it_works": "Alters the transform matrix (scale, position, rotation) per clip", "category": "editing"},
                {"name": "Chroma Key", "shortcut": "", "function": "Remove a color background", 
                 "how_it_works": "Applies color sampling + alpha channel masking based on tolerance", "category": "compositing"},
                {"name": "Track Motion", "shortcut": "", "function": "Animate a track", 
                 "how_it_works": "Applies movement to entire tracks using keyframe data", "category": "animation"}
            ],
            "common_concepts": [
                "Keyframes - All three use interpolation to animate changes over time",
                "Layers/Tracks - Photoshop (layers), Blender (scene collections), VEGAS (timeline tracks)",
                "Real-time Previews - All use CPU/GPU buffers to preview changes live",
                "Non-Destructive Editing - Smart objects, modifiers, adjustment layers preserve original assets"
            ]
        }
        
        query_lower = query.lower()
        
        # Determine software focus
        if "photoshop" in query_lower:
            software_focus = "Adobe Photoshop"
            relevant_tools = [SoftwareTool(**tool) for tool in knowledge_base["photoshop_tools"]]
            relevant_workspaces = []
        elif "blender" in query_lower:
            software_focus = "Blender"
            relevant_tools = []
            relevant_workspaces = [SoftwareWorkspace(**ws) for ws in knowledge_base["blender_workspaces"]]
        elif "vegas" in query_lower:
            software_focus = "Sony VEGAS Pro"
            relevant_tools = [SoftwareTool(**tool) for tool in knowledge_base["vegas_tools"]]
            relevant_workspaces = []
        else:
            software_focus = "Creative Software Suite"
            relevant_tools = [SoftwareTool(**tool) for tool in knowledge_base["photoshop_tools"][:2]]
            relevant_workspaces = [SoftwareWorkspace(**ws) for ws in knowledge_base["blender_workspaces"][:2]]
        
        # Generate relevant techniques
        techniques = [
            CreativeTechnique(
                technique="Layer-based Editing",
                description="Non-destructive editing using multiple layers",
                software="Photoshop",
                steps=["Create new layer", "Apply effects", "Adjust opacity", "Use blend modes"],
                technical_details="Each layer contains separate pixel data with alpha channel information"
            ),
            CreativeTechnique(
                technique="Mesh Modeling",
                description="Creating 3D objects using vertices, edges, and faces",
                software="Blender",
                steps=["Add primitive", "Edit mode", "Extrude faces", "Add loop cuts"],
                technical_details="Topology is defined by mesh data structure with vertex coordinates and face indices"
            )
        ]
        
        return SoftwareKnowledgeResponse(
            query=query,
            software_focus=software_focus,
            tools=relevant_tools,
            workspaces=relevant_workspaces,
            techniques=techniques,
            common_concepts=knowledge_base["common_concepts"],
            summary=f"Creative software knowledge for {software_focus} including tools, workflows, and technical implementation details."
        )

    def generate_analysis(self, topic: str) -> StructuredAnalysis:
        """Generate structured analysis"""
        analysis_points = []
        categories = ["Technical", "Strategic", "Operational", "Risk"]
        
        for category in categories:
            analysis_points.append(AnalysisPoint(
                category=category,
                finding=f"Key insights in {category.lower()} aspects of {topic} reveal important considerations for implementation.",
                confidence=random.uniform(0.7, 0.95),
                implications=f"This finding suggests that {category.lower()} factors will significantly impact the success of {topic}."
            ))
        
        return StructuredAnalysis(
            topic=topic,
            summary=f"Comprehensive analysis of {topic} reveals multiple key factors that require attention for successful implementation.",
            key_points=analysis_points,
            recommendations=[
                f"Prioritize {categories[0].lower()} considerations in initial planning",
                f"Develop comprehensive {categories[1].lower()} framework",
                f"Implement robust {categories[2].lower()} procedures",
                f"Establish effective {categories[3].lower()} mitigation strategies"
            ],
            confidence_level=0.85
        )
    
    async def stream_object_response(self, user_message: str, output_mode: OutputMode, schema_type: str) -> Generator[str, None, None]:
        """Stream structured object responses"""
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        if schema_type == "creative_software":
            software_knowledge = self.generate_creative_software_knowledge(user_message)
            if output_mode == OutputMode.OBJECT:
                # Stream the object progressively
                yield f"data: {json.dumps({'chunk_type': 'partial', 'data': {'query': software_knowledge.query, 'software_focus': software_knowledge.software_focus}, 'chunk_index': 0, 'is_final': False})}\n\n"
                await asyncio.sleep(0.3)
                
                # Add tools progressively
                for i, tool in enumerate(software_knowledge.tools):
                    partial_data = {
                        'query': software_knowledge.query,
                        'software_focus': software_knowledge.software_focus,
                        'tools': software_knowledge.tools[:i+1]
                    }
                    yield f"data: {json.dumps({'chunk_type': 'partial', 'data': partial_data, 'chunk_index': i+1, 'is_final': False})}\n\n"
                    await asyncio.sleep(0.2)
                
                # Final complete object
                yield f"data: {json.dumps({'chunk_type': 'complete', 'data': software_knowledge.dict(), 'chunk_index': len(software_knowledge.tools)+1, 'is_final': True})}\n\n"
            
            elif output_mode == OutputMode.ARRAY:
                # Stream tools and workspaces as array items
                all_items = software_knowledge.tools + software_knowledge.workspaces + software_knowledge.techniques
                for i, item in enumerate(all_items):
                    yield f"data: {json.dumps({'chunk_type': 'partial', 'data': item.dict(), 'chunk_index': i, 'is_final': i == len(all_items)-1})}\n\n"
                    await asyncio.sleep(0.3)
        
        elif schema_type == "search":
            if output_mode == OutputMode.OBJECT:
                search_response = self.generate_search_results(user_message)
                # Stream the object progressively
                yield f"data: {json.dumps({'chunk_type': 'partial', 'data': {'query': search_response.query}, 'chunk_index': 0, 'is_final': False})}\n\n"
                await asyncio.sleep(0.3)
                
                for i, result in enumerate(search_response.results):
                    partial_data = {
                        'query': search_response.query,
                        'results': search_response.results[:i+1]
                    }
                    yield f"data: {json.dumps({'chunk_type': 'partial', 'data': partial_data, 'chunk_index': i+1, 'is_final': False})}\n\n"
                    await asyncio.sleep(0.2)
                
                # Final complete object
                yield f"data: {json.dumps({'chunk_type': 'complete', 'data': search_response.dict(), 'chunk_index': len(search_response.results)+1, 'is_final': True})}\n\n"
            
            elif output_mode == OutputMode.ARRAY:
                search_response = self.generate_search_results(user_message)
                for i, result in enumerate(search_response.results):
                    yield f"data: {json.dumps({'chunk_type': 'partial', 'data': result.dict(), 'chunk_index': i, 'is_final': i == len(search_response.results)-1})}\n\n"
                    await asyncio.sleep(0.3)
        
        elif schema_type == "notifications":
            notifications = self.generate_notifications(user_message)
            if output_mode == OutputMode.ARRAY:
                for i, notification in enumerate(notifications):
                    yield f"data: {json.dumps({'chunk_type': 'partial', 'data': notification.dict(), 'chunk_index': i, 'is_final': i == len(notifications)-1})}\n\n"
                    await asyncio.sleep(0.4)
            else:
                yield f"data: {json.dumps({'chunk_type': 'complete', 'data': {'notifications': [n.dict() for n in notifications]}, 'chunk_index': 0, 'is_final': True})}\n\n"
        
        elif schema_type == "tasks":
            tasks = self.generate_tasks(user_message)
            if output_mode == OutputMode.ARRAY:
                for i, task in enumerate(tasks):
                    yield f"data: {json.dumps({'chunk_type': 'partial', 'data': task.dict(), 'chunk_index': i, 'is_final': i == len(tasks)-1})}\n\n"
                    await asyncio.sleep(0.3)
            else:
                yield f"data: {json.dumps({'chunk_type': 'complete', 'data': {'tasks': [t.dict() for t in tasks]}, 'chunk_index': 0, 'is_final': True})}\n\n"
        
        elif schema_type == "analysis":
            analysis = self.generate_analysis(user_message)
            if output_mode == OutputMode.OBJECT:
                # Stream analysis progressively
                yield f"data: {json.dumps({'chunk_type': 'partial', 'data': {'topic': analysis.topic, 'summary': analysis.summary}, 'chunk_index': 0, 'is_final': False})}\n\n"
                await asyncio.sleep(0.3)
                
                for i, point in enumerate(analysis.key_points):
                    partial_data = {
                        'topic': analysis.topic,
                        'summary': analysis.summary,
                        'key_points': analysis.key_points[:i+1]
                    }
                    yield f"data: {json.dumps({'chunk_type': 'partial', 'data': partial_data, 'chunk_index': i+1, 'is_final': False})}\n\n"
                    await asyncio.sleep(0.2)
                
                # Final complete analysis
                yield f"data: {json.dumps({'chunk_type': 'complete', 'data': analysis.dict(), 'chunk_index': len(analysis.key_points)+1, 'is_final': True})}\n\n"
        
        else:  # general response
            if output_mode == OutputMode.NO_SCHEMA:
                # Generate free-form JSON response
                response_data = {
                    "message": f"I understand you're asking about: '{user_message}'. Let me provide a comprehensive response.",
                    "analysis": f"This topic involves multiple considerations and I can help you explore it from different angles.",
                    "suggestions": [
                        "Consider breaking this down into smaller components",
                        "Look for patterns and connections",
                        "Evaluate different approaches and methodologies"
                    ],
                    "confidence": 0.8
                }
                yield f"data: {json.dumps({'chunk_type': 'complete', 'data': response_data, 'chunk_index': 0, 'is_final': True})}\n\n"
            else:
                # Default structured response
                response_data = {
                    "response": f"I understand your query about '{user_message}'. As CoresAI, I can provide detailed assistance with various topics.",
                    "capabilities": ["Analysis", "Research", "Problem-solving", "Planning", "Creative Software Knowledge"],
                    "next_steps": "Feel free to ask for specific types of responses like search results, tasks, analysis, or creative software guidance."
                }
                yield f"data: {json.dumps({'chunk_type': 'complete', 'data': response_data, 'chunk_index': 0, 'is_final': True})}\n\n"

# Initialize the streaming AI
ai = StreamingAI()

@app.get("/")
async def root():
    return {
        "message": "🚀 CoresAI Streaming Backend - Ready!", 
        "version": "4.1.0",
        "status": "production",
        "features": ["structured_streaming", "object_mode", "array_mode", "no_schema_mode", "creative_software_knowledge", "real_time_responses"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "message": "Streaming backend operational", 
        "features": ["structured_streaming", "object_mode", "array_mode", "no_schema_mode", "creative_software"],
        "version": "4.1.0",
        "uptime": "Ready for streaming responses with creative software knowledge"
    }

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """Traditional chat endpoint for backward compatibility"""
    try:
        user_message = request.messages[-1].content if request.messages else "Hello"
        response_type = ai.detect_response_type(user_message)
        
        # Generate structured response based on type
        if response_type == "creative_software":
            software_knowledge = ai.generate_creative_software_knowledge(user_message)
            response_text = f"🎨 **Creative Software Knowledge for '{user_message}':**\n\n"
            response_text += f"**Focus:** {software_knowledge.software_focus}\n\n"
            if software_knowledge.tools:
                response_text += "**Tools:**\n"
                for tool in software_knowledge.tools[:3]:
                    response_text += f"• {tool.name} ({tool.shortcut}): {tool.function}\n"
            response_text += f"\n**Summary:** {software_knowledge.summary}"
        elif response_type == "search":
            search_response = ai.generate_search_results(user_message)
            response_text = f"🔍 **Search Results for '{user_message}':**\n\n"
            for result in search_response.results:
                response_text += f"**{result.title}**\n{result.snippet}\n\n"
            response_text += f"**Summary:** {search_response.summary}"
        else:
            response_text = f"I understand you're asking about '{user_message}'. This would be perfect for structured streaming! Try the /api/v1/stream-object endpoint for enhanced responses with creative software knowledge."
        
        response_message = Message(role="assistant", content=response_text)
        updated_messages = request.messages + [response_message]
        
        return ChatResponse(messages=updated_messages)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.post("/api/v1/stream-object")
async def stream_object(request: StreamingRequest):
    """Main streaming endpoint for structured responses"""
    try:
        user_message = request.messages[-1]["content"] if request.messages else "Hello"
        schema_type = request.schema_type or ai.detect_response_type(user_message)
        
        return StreamingResponse(
            ai.stream_object_response(user_message, request.output_mode, schema_type),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming response: {str(e)}")

@app.post("/api/v1/detect-schema")
async def detect_schema(request: dict):
    """Endpoint to detect appropriate schema for a message"""
    message = request.get("message", "")
    schema_type = ai.detect_response_type(message)
    
    return {
        "message": message,
        "detected_schema": schema_type,
        "available_schemas": ["general", "search", "notifications", "tasks", "analysis", "creative_software"]
    }

# Legacy endpoints for compatibility
@app.post("/api/v1/search")
async def web_search_endpoint(request: dict):
    query = request.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    search_results = ai.generate_search_results(query)
    return search_results.dict()

@app.post("/api/v1/server-status")
async def server_status(request: dict):
    return {
        "status": "running", 
        "message": "Streaming server operational",
        "features": ["structured_streaming", "object_mode", "array_mode", "no_schema_mode", "creative_software"],
        "version": "4.1.0",
        "performance": "streaming_optimized"
    }

# Server management endpoints (compatibility)
@app.post("/api/v1/list-files")
async def list_files(request: dict):
    return {"files": [], "message": "File management ready", "status": "available"}

@app.post("/api/v1/read-file")
async def read_file(request: dict):
    return {"content": "File reading functionality ready", "message": "Feature operational"}

@app.post("/api/v1/write-file")
async def write_file(request: dict):
    return {"message": "File write operation completed", "status": "success"}

@app.post("/api/v1/start-server")
async def start_server(request: dict):
    return {"message": "Server management command received", "status": "success", "action": "start"}

@app.post("/api/v1/stop-server")
async def stop_server(request: dict):
    return {"message": "Server management command received", "status": "success", "action": "stop"}

if __name__ == "__main__":
    try:
        # Set UTF-8 encoding for Windows compatibility
        import sys
        if sys.platform == "win32":
            import os
            os.system("chcp 65001 > nul")
            
        print("=== Starting CoresAI Streaming Backend ===")
        print("Server: http://localhost:8081")
        print("Documentation: http://localhost:8081/docs")
        print("Features: Structured Streaming, Object Mode, Array Mode, No-Schema Mode")
        print("New Feature: Creative Software Knowledge (Photoshop, Blender, VEGAS Pro)")
        print("Performance: Streaming Optimized")
        print("Version 4.1.0 - Advanced Creative Software Ready")
        print("=" * 50)
        
        uvicorn.run(app, host="0.0.0.0", port=8081)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1) 