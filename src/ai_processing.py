"""
CoresAI Processing Module
Handles AI chat processing and responses
"""

import logging
from typing import List, Dict
import json
import aiohttp
from .config import API_URL

logger = logging.getLogger(__name__)

async def process_chat_message(message: str, history: List[Dict[str, str]]) -> str:
    """Process chat messages with AI"""
    try:
        # Format conversation history
        formatted_history = []
        for entry in history[-5:]:  # Keep last 5 messages for context
            formatted_history.append({
                "role": entry["role"],
                "content": entry["content"]
            })

        # Prepare request
        request_data = {
            "messages": formatted_history,
            "max_tokens": 500,
            "temperature": 0.7,
            "stream": False
        }

        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/chat",
                json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["response"]
                else:
                    error_data = await response.text()
                    logger.error(f"API error: {error_data}")
                    return "I encountered an error processing your message. Please try again."

    except Exception as e:
        logger.error(f"Error in process_chat_message: {e}")
        return "Sorry, I'm having trouble processing your request right now." 