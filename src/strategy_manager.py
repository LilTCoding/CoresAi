"""
CoresAI Strategy Manager Module
Handles trading strategy management and execution
"""

import logging
from typing import Dict, Any, List, Optional
import aiohttp
import json
from datetime import datetime
from .config import API_URL

logger = logging.getLogger(__name__)

async def manage_strategy(
    action: str,
    user_id: str,
    name: Optional[str] = None,
    parameters: Optional[str] = None
) -> Dict[str, Any]:
    """Manage trading strategies"""
    try:
        if action == "list":
            return await list_strategies(user_id)
        elif action == "create":
            return await create_strategy(user_id, name, parameters)
        elif action == "delete":
            return await delete_strategy(user_id, name)
        else:
            raise ValueError(f"Invalid action: {action}")

    except Exception as e:
        logger.error(f"Error in manage_strategy: {e}")
        return {
            "status": "error",
            "message": f"Strategy management failed: {str(e)}"
        }

async def list_strategies(user_id: str) -> Dict[str, Any]:
    """List available trading strategies"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/strategy/list",
                params={"user_id": user_id}
            ) as response:
                if response.status == 200:
                    strategies = await response.json()
                    return {
                        "status": "success",
                        "strategies": strategies["strategies"]
                    }
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error listing strategies: {e}")
        return {
            "status": "error",
            "message": f"Failed to list strategies: {str(e)}"
        }

async def create_strategy(
    user_id: str,
    name: str,
    parameters: str
) -> Dict[str, Any]:
    """Create a new trading strategy"""
    try:
        # Parse strategy parameters
        params = json.loads(parameters) if parameters else {}
        
        # Prepare strategy request
        strategy_request = {
            "user_id": user_id,
            "name": name,
            "parameters": params,
            "created_at": datetime.now().isoformat()
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/strategy/create",
                json=strategy_request
            ) as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "message": f"Strategy '{name}' created successfully"
                    }
                else:
                    raise Exception(f"API error: {await response.text()}")

    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Invalid strategy parameters format"
        }
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        return {
            "status": "error",
            "message": f"Failed to create strategy: {str(e)}"
        }

async def delete_strategy(user_id: str, name: str) -> Dict[str, Any]:
    """Delete a trading strategy"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{API_URL}/api/strategy/delete",
                json={"user_id": user_id, "name": name}
            ) as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "message": f"Strategy '{name}' deleted successfully"
                    }
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error deleting strategy: {e}")
        return {
            "status": "error",
            "message": f"Failed to delete strategy: {str(e)}"
        }

async def get_strategy_performance(
    user_id: str,
    strategy_name: str,
    timeframe: str = "1m"
) -> Dict[str, Any]:
    """Get strategy performance metrics"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/strategy/performance",
                params={
                    "user_id": user_id,
                    "strategy_name": strategy_name,
                    "timeframe": timeframe
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error fetching strategy performance: {e}")
        raise

async def update_strategy(
    user_id: str,
    name: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """Update strategy parameters"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/strategy/update",
                json={
                    "user_id": user_id,
                    "name": name,
                    "updates": updates
                }
            ) as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "message": f"Strategy '{name}' updated successfully"
                    }
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error updating strategy: {e}")
        return {
            "status": "error",
            "message": f"Failed to update strategy: {str(e)}"
        } 