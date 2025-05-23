import numpy as np
from typing import List, Dict, Any, Optional, Union
import torch
import json
import os
from datetime import datetime
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_analysis_results(results: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Save analysis results to a JSON file.
    """
    try:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_results_{timestamp}.json"
        
        # Ensure the directory exists
        output_dir = Path("data/analysis_results")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        # Convert numpy arrays to lists for JSON serialization
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, np.ndarray):
                serializable_results[key] = value.tolist()
            elif isinstance(value, torch.Tensor):
                serializable_results[key] = value.cpu().numpy().tolist()
            else:
                serializable_results[key] = value
        
        with open(filepath, 'w') as f:
            json.dump(serializable_results, f, indent=4)
        
        logger.info(f"Analysis results saved to {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error saving analysis results: {e}")
        raise

def load_training_data(filepath: str) -> List[Dict[str, Any]]:
    """
    Load training data from a JSON file.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Validate data format
        if not isinstance(data, list):
            raise ValueError("Training data must be a list of dictionaries")
        
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("Each training item must be a dictionary")
            if "text" not in item or "target" not in item:
                raise ValueError("Each training item must contain 'text' and 'target' fields")
        
        logger.info(f"Successfully loaded {len(data)} training samples from {filepath}")
        return data
    except Exception as e:
        logger.error(f"Error loading training data: {e}")
        raise

def preprocess_text(text: str) -> str:
    """
    Preprocess text for model input.
    """
    try:
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters (keep alphanumeric and basic punctuation)
        text = ''.join(char for char in text if char.isalnum() or char in ' .,!?')
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        return text
    except Exception as e:
        logger.error(f"Error preprocessing text: {e}")
        return text

def calculate_metrics(predictions: np.ndarray, targets: np.ndarray) -> Dict[str, float]:
    """
    Calculate various metrics for model evaluation.
    """
    try:
        # Ensure inputs are numpy arrays
        predictions = np.asarray(predictions)
        targets = np.asarray(targets)
        
        # Basic regression metrics
        mse = np.mean((predictions - targets) ** 2)
        mae = np.mean(np.abs(predictions - targets))
        rmse = np.sqrt(mse)
        
        # R-squared score
        ss_res = np.sum((targets - predictions) ** 2)
        ss_tot = np.sum((targets - np.mean(targets)) ** 2)
        r2 = 1 - (ss_res / (ss_tot + 1e-10))
        
        # Explained variance score
        explained_variance = 1 - np.var(targets - predictions) / (np.var(targets) + 1e-10)
        
        return {
            "mse": float(mse),
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "explained_variance": float(explained_variance)
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            "mse": float('nan'),
            "mae": float('nan'),
            "rmse": float('nan'),
            "r2": float('nan'),
            "explained_variance": float('nan')
        }

def create_experiment_log(experiment_name: str, parameters: Dict[str, Any]) -> str:
    """
    Create a log file for an experiment.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = Path("experiment_logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{experiment_name}_{timestamp}.json"
        
        log_data = {
            "experiment_name": experiment_name,
            "timestamp": timestamp,
            "parameters": parameters,
            "system_info": {
                "python_version": os.sys.version,
                "platform": os.sys.platform,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else None
            }
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=4)
        
        logger.info(f"Created experiment log at {log_file}")
        return str(log_file)
    except Exception as e:
        logger.error(f"Error creating experiment log: {e}")
        raise

def validate_model_input(text: str) -> bool:
    """
    Validate input text for the model.
    """
    try:
        if not isinstance(text, str):
            return False
        
        if len(text.strip()) == 0:
            return False
        
        if len(text) > 10000:  # Maximum text length
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating model input: {e}")
        return False

def format_model_output(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format model output for consistent response structure.
    """
    try:
        formatted = {}
        
        # Ensure all numpy arrays are converted to lists
        for key, value in output.items():
            if isinstance(value, np.ndarray):
                formatted[key] = value.tolist()
            elif isinstance(value, torch.Tensor):
                formatted[key] = value.cpu().numpy().tolist()
            else:
                formatted[key] = value
        
        return formatted
    except Exception as e:
        logger.error(f"Error formatting model output: {e}")
        return {"error": str(e)} 