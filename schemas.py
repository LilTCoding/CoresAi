from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union
from enum import Enum

class OutputMode(str, Enum):
    OBJECT = "object"
    ARRAY = "array"
    NO_SCHEMA = "no-schema"

class SearchResult(BaseModel):
    title: str = Field(description="Title of the search result")
    snippet: str = Field(description="Brief description or snippet")
    url: str = Field(description="URL of the source")
    relevance_score: float = Field(description="Relevance score from 0 to 1")

class WebSearchResponse(BaseModel):
    query: str = Field(description="The search query")
    results: List[SearchResult] = Field(description="List of search results")
    summary: str = Field(description="AI summary of the search results")

class Notification(BaseModel):
    name: str = Field(description="Name of a person")
    message: str = Field(description="Notification message without emojis")
    timestamp: str = Field(description="Timestamp of the notification")
    priority: str = Field(description="Priority level: low, medium, high")

class TaskItem(BaseModel):
    title: str = Field(description="Task title")
    description: str = Field(description="Detailed task description")
    priority: str = Field(description="Priority: low, medium, high")
    estimated_time: str = Field(description="Estimated completion time")
    category: str = Field(description="Task category")

class AnalysisPoint(BaseModel):
    category: str = Field(description="Analysis category")
    finding: str = Field(description="Key finding or insight")
    confidence: float = Field(description="Confidence level from 0 to 1")
    implications: str = Field(description="Implications of this finding")

class StructuredAnalysis(BaseModel):
    topic: str = Field(description="Topic being analyzed")
    summary: str = Field(description="Executive summary")
    key_points: List[AnalysisPoint] = Field(description="Key analysis points")
    recommendations: List[str] = Field(description="Actionable recommendations")
    confidence_level: float = Field(description="Overall confidence in analysis")

# Creative Software Knowledge Models
class SoftwareTool(BaseModel):
    name: str = Field(description="Tool name")
    shortcut: Optional[str] = Field(description="Keyboard shortcut")
    function: str = Field(description="What the tool does")
    how_it_works: str = Field(description="Technical explanation of how it works")
    category: str = Field(description="Tool category (selection, painting, modeling, etc.)")

class SoftwareWorkspace(BaseModel):
    name: str = Field(description="Workspace/interface name")
    purpose: str = Field(description="Main purpose of this workspace")
    how_it_works: str = Field(description="Technical explanation")
    software: str = Field(description="Which software (Photoshop, Blender, VEGAS)")

class CreativeTechnique(BaseModel):
    technique: str = Field(description="Technique name")
    description: str = Field(description="What the technique does")
    software: str = Field(description="Which software it applies to")
    steps: List[str] = Field(description="Step-by-step process")
    technical_details: str = Field(description="Under-the-hood explanation")

class SoftwareKnowledgeResponse(BaseModel):
    query: str = Field(description="The user's query")
    software_focus: str = Field(description="Primary software discussed")
    tools: List[SoftwareTool] = Field(description="Relevant tools")
    workspaces: List[SoftwareWorkspace] = Field(description="Relevant workspaces")
    techniques: List[CreativeTechnique] = Field(description="Relevant techniques")
    common_concepts: List[str] = Field(description="Shared concepts across software")
    summary: str = Field(description="AI summary of the creative software knowledge")

class StreamingRequest(BaseModel):
    messages: List[dict]
    output_mode: OutputMode = OutputMode.OBJECT
    schema_type: str = "general"  # general, search, notifications, tasks, analysis, creative_software
    context: Optional[str] = None

class StreamingChunk(BaseModel):
    chunk_type: str  # "partial", "complete", "error"
    data: Any
    chunk_index: int
    is_final: bool = False 