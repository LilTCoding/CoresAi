from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from ..models.enhanced_ai import EnhancedAI
from ..models.voice_processor import VoiceProcessor
from ..models.server_manager import ServerManager
from ..config.settings import settings
from ..utils.helpers import save_analysis_results
from ..models.ai_brain import AIBrain
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Advanced AI Assistant with Windows and System Awareness",
    version="1.0.0"
)

# Initialize the AI model and voice processor
ai_model = EnhancedAI()
voice_processor = VoiceProcessor()
server_manager = ServerManager()
ai_brain = AIBrain()

class UserInput(BaseModel):
    text: str
    use_voice: bool = False

class AIResponse(BaseModel):
    response: str
    system_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SystemStatus(BaseModel):
    system_info: Dict[str, Any]
    conversation_history: list
    timestamp: str

class TextInput(BaseModel):
    text: str
    options: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    embeddings: list
    confidence: float
    analysis: Dict[str, Any]

class TrainingData(BaseModel):
    text: str
    target: List[float]

class TrainingResponse(BaseModel):
    status: str
    metrics_history: Optional[Dict[str, Any]] = None
    log_file: Optional[str] = None
    error: Optional[str] = None

class EvaluationResponse(BaseModel):
    status: str
    metrics: Optional[Dict[str, float]] = None
    predictions: Optional[List[float]] = None
    targets: Optional[List[float]] = None
    error: Optional[str] = None

class VoiceInput(BaseModel):
    text: str
    save_output: bool = True

class VoiceResponse(BaseModel):
    status: str
    audio: Optional[List[float]] = None
    sample_rate: Optional[int] = None
    output_file: Optional[str] = None
    error: Optional[str] = None

class AutoSetupRequest(BaseModel):
    game: str
    description: str

class AutoSetupResponse(BaseModel):
    status: str
    logs: Optional[List[str]] = None
    blueprint: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class FileListRequest(BaseModel):
    game: str
    subdir: str = ""

class FileReadRequest(BaseModel):
    game: str
    filepath: str

class FileWriteRequest(BaseModel):
    game: str
    filepath: str
    content: str

class FileDeleteRequest(BaseModel):
    game: str
    filepath: str

class ServerControlRequest(BaseModel):
    game: str

class BlueprintRequest(BaseModel):
    game: str
    description: str

class ModSuggestionRequest(BaseModel):
    game: str
    description: str

class StepHelpRequest(BaseModel):
    game: str
    current_step: str
    context: Dict[str, Any]

class FileEditRequest(BaseModel):
    game: str
    filepath: str
    instruction: str

@app.post(f"/{settings.API_V1_STR}/chat", response_model=AIResponse)
async def chat(input_data: UserInput):
    """Process user input and generate a response."""
    try:
        logger.info(f"Processing input: {input_data.text}")
        
        # Process input through AI model
        result = ai_model.process_input(input_data.text)
        
        # If voice is requested, synthesize the response
        if input_data.use_voice:
            try:
                audio = voice_processor.process_text_to_speech(result['response'])
                # You might want to save the audio file or return it in the response
            except Exception as e:
                logger.error(f"Error in voice synthesis: {str(e)}")
                # Continue without voice if there's an error
        
        return result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(f"/{settings.API_V1_STR}/system-status", response_model=SystemStatus)
async def get_system_status():
    """Get the current system status and conversation history."""
    try:
        return ai_model.get_system_status()
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(f"/{settings.API_V1_STR}/health")
async def health_check():
    """Check the health of the AI system."""
    try:
        return {
            "status": "healthy",
            "ai_model": "operational",
            "voice_processor": "operational",
            "system_awareness": "operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/analyze", response_model=AnalysisResponse)
async def analyze_text(input_data: TextInput):
    """
    Analyze text using the AI model and return insights.
    """
    try:
        logger.info(f"Processing text analysis request: {input_data.text[:100]}...")
        result = ai_model.process_text(input_data.text)
        
        if "error" in result:
            logger.error(f"Error in text analysis: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Save analysis results if requested
        if input_data.options and input_data.options.get("save_results", False):
            filename = save_analysis_results(result)
            logger.info(f"Analysis results saved to {filename}")
        
        return result
    except Exception as e:
        logger.error(f"Unexpected error in analyze_text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/train", response_model=TrainingResponse)
async def train_model(
    training_data: List[TrainingData],
    background_tasks: BackgroundTasks,
    epochs: Optional[int] = None
):
    """
    Train the AI model with provided data.
    """
    try:
        logger.info(f"Starting model training with {len(training_data)} samples")
        
        # Convert training data to the format expected by the model
        formatted_data = [
            {"text": item.text, "target": item.target}
            for item in training_data
        ]
        
        # Train the model
        result = ai_model.train(formatted_data, epochs)
        
        if result["status"] == "error":
            logger.error(f"Training failed: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("Training completed successfully")
        return result
    except Exception as e:
        logger.error(f"Unexpected error in train_model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/evaluate", response_model=EvaluationResponse)
async def evaluate_model(test_data: List[TrainingData]):
    """
    Evaluate the model on test data.
    """
    try:
        logger.info(f"Starting model evaluation with {len(test_data)} samples")
        
        # Convert test data to the format expected by the model
        formatted_data = [
            {"text": item.text, "target": item.target}
            for item in test_data
        ]
        
        # Evaluate the model
        result = ai_model.evaluate(formatted_data)
        
        if result["status"] == "error":
            logger.error(f"Evaluation failed: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info("Evaluation completed successfully")
        return result
    except Exception as e:
        logger.error(f"Unexpected error in evaluate_model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/save-model")
async def save_model(path: str):
    """
    Save the current model state to disk.
    """
    try:
        logger.info(f"Saving model to {path}")
        ai_model.save_model(path)
        return {"status": "success", "message": f"Model saved to {path}"}
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/load-model")
async def load_model(path: str):
    """
    Load a model state from disk.
    """
    try:
        logger.info(f"Loading model from {path}")
        ai_model.load_model(path)
        return {"status": "success", "message": f"Model loaded from {path}"}
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/synthesize-voice", response_model=VoiceResponse)
async def synthesize_voice(input_data: VoiceInput):
    """
    Synthesize text to speech using Cortana-like voice.
    """
    try:
        logger.info(f"Processing voice synthesis request: {input_data.text[:100]}...")
        
        # First analyze the text
        analysis_result = ai_model.process_text(input_data.text)
        if "error" in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result["error"])
        
        # Then synthesize voice
        result = voice_processor.process_text_to_speech(
            input_data.text,
            save_output=input_data.save_output
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        logger.error(f"Unexpected error in synthesize_voice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(f"{settings.API_V1_STR}/voice-health")
async def voice_health_check():
    """
    Health check endpoint for voice synthesis.
    """
    try:
        voice_status = {
            "status": "healthy",
            "reference_voice_loaded": voice_processor.reference_audio is not None,
            "device": str(voice_processor.device),
            "sample_rate": voice_processor.sample_rate
        }
        logger.info(f"Voice health check: {voice_status}")
        return voice_status
    except Exception as e:
        logger.error(f"Voice health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"/{settings.API_V1_STR}/auto-setup-server", response_model=AutoSetupResponse)
async def auto_setup_server(request: AutoSetupRequest):
    """Auto-setup a game server based on user description."""
    result = server_manager.auto_setup_server(request.game, request.description)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/list-files")
async def list_files(request: FileListRequest):
    result = server_manager.list_files(request.game, request.subdir)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/read-file")
async def read_file(request: FileReadRequest):
    result = server_manager.read_file(request.game, request.filepath)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/write-file")
async def write_file(request: FileWriteRequest):
    result = server_manager.write_file(request.game, request.filepath, request.content)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/delete-file")
async def delete_file(request: FileDeleteRequest):
    result = server_manager.delete_file(request.game, request.filepath)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/start-server")
async def start_server(request: ServerControlRequest):
    result = server_manager.start_server(request.game)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/stop-server")
async def stop_server(request: ServerControlRequest):
    result = server_manager.stop_server(request.game)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/restart-server")
async def restart_server(request: ServerControlRequest):
    result = server_manager.restart_server(request.game)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/server-status")
async def server_status(request: ServerControlRequest):
    result = server_manager.server_status(request.game)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post(f"/{settings.API_V1_STR}/generate-blueprint")
async def generate_blueprint(request: BlueprintRequest):
    return ai_brain.generate_blueprint(request.game, request.description)

@app.post(f"/{settings.API_V1_STR}/suggest-mods")
async def suggest_mods(request: ModSuggestionRequest):
    return {"suggested_mods": ai_brain.suggest_mods(request.game, request.description)}

@app.post(f"/{settings.API_V1_STR}/step-by-step-help")
async def step_by_step_help(request: StepHelpRequest):
    return {"help": ai_brain.step_by_step_help(request.game, request.current_step, request.context)}

@app.post(f"/{settings.API_V1_STR}/ai-file-edit")
async def ai_file_edit(request: FileEditRequest):
    return ai_brain.handle_file_edit(request.game, request.filepath, request.instruction)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 