import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from ..config.settings import settings
from ..utils.helpers import calculate_metrics, create_experiment_log
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAIModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize the AI model with pre-trained weights."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
            self.model = AutoModel.from_pretrained("gpt2").to(self.device)
            logger.info(f"Model initialized successfully on {self.device}")
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            # Fallback to a simpler model if needed
            self.model = nn.Sequential(
                nn.Linear(768, 512),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(256, 128)
            ).to(self.device)
            logger.info("Using fallback model architecture")
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text input and return AI analysis."""
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return {
                "embeddings": embeddings.cpu().numpy(),
                "confidence": self._calculate_confidence(embeddings),
                "analysis": self._analyze_output(embeddings)
            }
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return {"error": str(e)}
    
    def _calculate_confidence(self, embeddings: torch.Tensor) -> float:
        """Calculate confidence score for the model's output."""
        try:
            # Calculate confidence based on embedding variance and magnitude
            variance = torch.var(embeddings, dim=1)
            magnitude = torch.norm(embeddings, dim=1)
            confidence = torch.sigmoid(magnitude / (variance + 1e-6))
            return float(confidence.mean().item())
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.0
    
    def _analyze_output(self, embeddings: torch.Tensor) -> Dict[str, Any]:
        """Analyze the model's output and provide insights."""
        try:
            return {
                "semantic_similarity": self._calculate_semantic_similarity(embeddings),
                "feature_importance": self._get_feature_importance(embeddings),
                "embedding_stats": {
                    "mean": float(embeddings.mean().item()),
                    "std": float(embeddings.std().item()),
                    "max": float(embeddings.max().item()),
                    "min": float(embeddings.min().item())
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing output: {e}")
            return {"error": str(e)}
    
    def _calculate_semantic_similarity(self, embeddings: torch.Tensor) -> float:
        """Calculate semantic similarity score."""
        try:
            # Normalize embeddings
            normalized = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            # Calculate cosine similarity matrix
            similarity_matrix = torch.mm(normalized, normalized.t())
            # Return average similarity (excluding self-similarity)
            mask = torch.ones_like(similarity_matrix) - torch.eye(similarity_matrix.size(0), device=self.device)
            return float((similarity_matrix * mask).sum() / mask.sum().item())
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def _get_feature_importance(self, embeddings: torch.Tensor) -> List[float]:
        """Get feature importance scores."""
        try:
            # Calculate feature importance using variance
            importance = torch.var(embeddings, dim=0)
            # Normalize importance scores
            importance = importance / importance.sum()
            return importance.cpu().numpy().tolist()
        except Exception as e:
            logger.error(f"Error calculating feature importance: {e}")
            return []
    
    def train(self, training_data: List[Dict[str, Any]], epochs: Optional[int] = None) -> Dict[str, Any]:
        """Train the model on provided data."""
        if epochs is None:
            epochs = settings.EPOCHS
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=settings.LEARNING_RATE)
        criterion = nn.MSELoss()
        
        # Initialize training metrics
        metrics_history = {
            "train_loss": [],
            "val_loss": [],
            "train_metrics": [],
            "val_metrics": []
        }
        
        # Create experiment log
        experiment_params = {
            "epochs": epochs,
            "batch_size": settings.BATCH_SIZE,
            "learning_rate": settings.LEARNING_RATE,
            "device": str(self.device)
        }
        log_file = create_experiment_log("model_training", experiment_params)
        
        try:
            for epoch in range(epochs):
                self.model.train()
                total_loss = 0
                batch_metrics = []
                
                # Training loop
                for batch in training_data:
                    optimizer.zero_grad()
                    
                    # Prepare batch data
                    inputs = self.tokenizer(
                        batch["text"],
                        return_tensors="pt",
                        padding=True,
                        truncation=True
                    ).to(self.device)
                    
                    targets = torch.tensor(batch["target"], device=self.device)
                    
                    # Forward pass
                    outputs = self.model(**inputs)
                    predictions = outputs.last_hidden_state.mean(dim=1)
                    
                    # Calculate loss
                    loss = criterion(predictions, targets)
                    
                    # Backward pass
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                    
                    # Calculate batch metrics
                    batch_metrics.append(calculate_metrics(
                        predictions.detach().cpu().numpy(),
                        targets.cpu().numpy()
                    ))
                
                # Calculate epoch metrics
                epoch_loss = total_loss / len(training_data)
                epoch_metrics = {
                    metric: np.mean([batch[metric] for batch in batch_metrics])
                    for metric in batch_metrics[0].keys()
                }
                
                metrics_history["train_loss"].append(epoch_loss)
                metrics_history["train_metrics"].append(epoch_metrics)
                
                # Log progress
                if (epoch + 1) % 10 == 0:
                    logger.info(f"Epoch [{epoch+1}/{epochs}]")
                    logger.info(f"Loss: {epoch_loss:.4f}")
                    logger.info(f"Metrics: {epoch_metrics}")
            
            return {
                "status": "success",
                "metrics_history": metrics_history,
                "log_file": log_file
            }
            
        except Exception as e:
            logger.error(f"Error during training: {e}")
            return {
                "status": "error",
                "error": str(e),
                "log_file": log_file
            }
    
    def evaluate(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate the model on test data."""
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        try:
            with torch.no_grad():
                for batch in test_data:
                    inputs = self.tokenizer(
                        batch["text"],
                        return_tensors="pt",
                        padding=True,
                        truncation=True
                    ).to(self.device)
                    
                    targets = torch.tensor(batch["target"], device=self.device)
                    
                    outputs = self.model(**inputs)
                    predictions = outputs.last_hidden_state.mean(dim=1)
                    
                    all_predictions.append(predictions.cpu().numpy())
                    all_targets.append(targets.cpu().numpy())
            
            # Concatenate all predictions and targets
            predictions = np.concatenate(all_predictions)
            targets = np.concatenate(all_targets)
            
            # Calculate evaluation metrics
            metrics = calculate_metrics(predictions, targets)
            
            return {
                "status": "success",
                "metrics": metrics,
                "predictions": predictions.tolist(),
                "targets": targets.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def save_model(self, path: str):
        """Save the model to disk."""
        try:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'tokenizer': self.tokenizer,
                'config': {
                    'device': str(self.device),
                    'model_type': type(self.model).__name__
                }
            }, path)
            logger.info(f"Model saved successfully to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    def load_model(self, path: str):
        """Load the model from disk."""
        try:
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.tokenizer = checkpoint['tokenizer']
            logger.info(f"Model loaded successfully from {path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise 