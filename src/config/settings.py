from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Advanced AI System"
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Model Settings
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    MODEL_SAVE_DIR: str = "models/saved"
    MODEL_LOAD_DIR: str = "models/pretrained"
    
    # Training Settings
    BATCH_SIZE: int = 32
    LEARNING_RATE: float = 0.001
    EPOCHS: int = 100
    VALIDATION_SPLIT: float = 0.2
    EARLY_STOPPING_PATIENCE: int = 5
    GRADIENT_CLIP_VALUE: float = 1.0
    
    # Data Settings
    DATA_DIR: str = "data"
    TRAINING_DATA_DIR: str = "data/training"
    TEST_DATA_DIR: str = "data/test"
    ANALYSIS_RESULTS_DIR: str = "data/analysis_results"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    EXPERIMENT_LOGS_DIR: str = "experiment_logs"
    
    # Security Settings
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: Optional[str] = os.getenv("API_KEY")
    CORS_ORIGINS: list = ["*"]
    
    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour
    
    # Performance Settings
    NUM_WORKERS: int = 4
    MAX_CONNECTIONS: int = 100
    TIMEOUT: int = 30
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration parameters."""
        return {
            "max_tokens": self.MAX_TOKENS,
            "temperature": self.TEMPERATURE,
            "batch_size": self.BATCH_SIZE,
            "learning_rate": self.LEARNING_RATE,
            "epochs": self.EPOCHS
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration parameters."""
        return {
            "host": self.API_HOST,
            "port": self.API_PORT,
            "debug": self.DEBUG,
            "workers": self.NUM_WORKERS,
            "timeout": self.TIMEOUT
        }
    
    def create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.DATA_DIR,
            self.TRAINING_DATA_DIR,
            self.TEST_DATA_DIR,
            self.ANALYSIS_RESULTS_DIR,
            self.MODEL_SAVE_DIR,
            self.MODEL_LOAD_DIR,
            self.LOG_DIR,
            self.EXPERIMENT_LOGS_DIR
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
settings.create_directories() 