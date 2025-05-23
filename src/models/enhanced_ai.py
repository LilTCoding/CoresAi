from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from .system_awareness import SystemAwareness
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch

class EnhancedAI:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system_awareness = SystemAwareness()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize the language model
        self.model_name = "microsoft/DialoGPT-medium"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Initialize system knowledge
        self.system_knowledge = {
            'windows': self._load_windows_knowledge(),
            'computer': self._load_computer_knowledge()
        }

    def _load_windows_knowledge(self) -> Dict[str, Any]:
        """Load Windows-specific knowledge."""
        return {
            'version': self.system_awareness.get_specific_info('os'),
            'features': {
                'security': self.system_awareness.get_specific_info('security'),
                'updates': self.system_awareness.get_specific_info('os').get('last_update', 'Unknown'),
                'edition': self.system_awareness.get_specific_info('os').get('windows_edition', 'Unknown')
            }
        }

    def _load_computer_knowledge(self) -> Dict[str, Any]:
        """Load computer-specific knowledge."""
        return {
            'hardware': self.system_awareness.get_specific_info('hardware'),
            'software': self.system_awareness.get_specific_info('software'),
            'performance': self.system_awareness.get_specific_info('performance')
        }

    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input and generate a response."""
        try:
            # Update system knowledge
            self.system_knowledge['windows'] = self._load_windows_knowledge()
            self.system_knowledge['computer'] = self._load_computer_knowledge()
            
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Generate response
            response = self._generate_response(user_input)
            
            # Add response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return {
                'response': response,
                'system_info': self.system_knowledge,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error processing input: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _generate_response(self, user_input: str) -> str:
        """Generate a response based on user input and system knowledge."""
        try:
            # Check if the input is about Windows or the computer
            if self._is_windows_related(user_input):
                return self._generate_windows_response(user_input)
            elif self._is_computer_related(user_input):
                return self._generate_computer_response(user_input)
            else:
                return self._generate_general_response(user_input)
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."

    def _is_windows_related(self, text: str) -> bool:
        """Check if the input is related to Windows."""
        windows_keywords = [
            'windows', 'update', 'security', 'firewall', 'antivirus',
            'settings', 'control panel', 'system', 'registry', 'driver'
        ]
        return any(keyword in text.lower() for keyword in windows_keywords)

    def _is_computer_related(self, text: str) -> bool:
        """Check if the input is related to the computer."""
        computer_keywords = [
            'cpu', 'memory', 'disk', 'gpu', 'hardware', 'software',
            'performance', 'process', 'network', 'temperature'
        ]
        return any(keyword in text.lower() for keyword in computer_keywords)

    def _generate_windows_response(self, user_input: str) -> str:
        """Generate a response for Windows-related queries."""
        # Get relevant Windows information
        windows_info = self.system_knowledge['windows']
        
        # Generate response using the language model
        input_text = f"Windows Information: {windows_info}\nUser Query: {user_input}\nResponse:"
        response_ids = self.model.generate(
            self.tokenizer.encode(input_text, return_tensors='pt').to(self.device),
            max_length=200,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.7
        )
        
        return self.tokenizer.decode(response_ids[0], skip_special_tokens=True)

    def _generate_computer_response(self, user_input: str) -> str:
        """Generate a response for computer-related queries."""
        # Get relevant computer information
        computer_info = self.system_knowledge['computer']
        
        # Generate response using the language model
        input_text = f"Computer Information: {computer_info}\nUser Query: {user_input}\nResponse:"
        response_ids = self.model.generate(
            self.tokenizer.encode(input_text, return_tensors='pt').to(self.device),
            max_length=200,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.7
        )
        
        return self.tokenizer.decode(response_ids[0], skip_special_tokens=True)

    def _generate_general_response(self, user_input: str) -> str:
        """Generate a response for general queries."""
        # Generate response using the language model
        input_text = f"User Query: {user_input}\nResponse:"
        response_ids = self.model.generate(
            self.tokenizer.encode(input_text, return_tensors='pt').to(self.device),
            max_length=200,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.7
        )
        
        return self.tokenizer.decode(response_ids[0], skip_special_tokens=True)

    def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status."""
        return {
            'system_info': self.system_knowledge,
            'conversation_history': self.conversation_history,
            'timestamp': datetime.now().isoformat()
        } 