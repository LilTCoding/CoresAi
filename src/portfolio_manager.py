"""
CoresAI Portfolio Manager Module
Handles portfolio tracking and management
"""

import logging
from typing import Dict, Any
import aiohttp
from datetime import datetime
from .config import API_URL

logger = logging.getLogger(__name__)

async def get_portfolio(user_id: str) -> Dict[str, Any]:
    """Get user's portfolio data"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/portfolio",
                params={"user_id": user_id}
            ) as response:
                if response.status == 200:
                    portfolio_data = await response.json()
                    
                    # Calculate additional metrics
                    total_pl = calculate_total_pl(portfolio_data)
                    daily_pl = calculate_daily_pl(portfolio_data)
                    
                    return {
                        "total_balance": portfolio_data["total_balance"],
                        "available_cash": portfolio_data["available_cash"],
                        "invested_amount": portfolio_data["invested_amount"],
                        "holdings": portfolio_data["holdings"],
                        "daily_pl": daily_pl["value"],
                        "daily_pl_percent": daily_pl["percent"],
                        "total_pl": total_pl["value"],
                        "total_pl_percent": total_pl["percent"]
                    }
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        raise

async def update_portfolio(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update portfolio settings"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/portfolio/update",
                json={"user_id": user_id, "updates": updates}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error updating portfolio: {e}")
        raise

def calculate_total_pl(portfolio_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate total profit/loss"""
    try:
        total_value = portfolio_data["total_balance"]
        initial_value = portfolio_data["initial_investment"]
        
        pl_value = total_value - initial_value
        pl_percent = (pl_value / initial_value) * 100 if initial_value > 0 else 0
        
        return {
            "value": pl_value,
            "percent": pl_percent
        }
    except Exception as e:
        logger.error(f"Error calculating total P/L: {e}")
        return {"value": 0, "percent": 0}

def calculate_daily_pl(portfolio_data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate daily profit/loss"""
    try:
        current_value = portfolio_data["total_balance"]
        previous_value = portfolio_data["previous_day_balance"]
        
        pl_value = current_value - previous_value
        pl_percent = (pl_value / previous_value) * 100 if previous_value > 0 else 0
        
        return {
            "value": pl_value,
            "percent": pl_percent
        }
    except Exception as e:
        logger.error(f"Error calculating daily P/L: {e}")
        return {"value": 0, "percent": 0}

async def get_portfolio_history(
    user_id: str,
    timeframe: str = "1m"
) -> Dict[str, Any]:
    """Get historical portfolio performance"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/portfolio/history",
                params={"user_id": user_id, "timeframe": timeframe}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error fetching portfolio history: {e}")
        raise

async def get_portfolio_analytics(user_id: str) -> Dict[str, Any]:
    """Get portfolio analytics and insights"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/portfolio/analytics",
                params={"user_id": user_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error fetching portfolio analytics: {e}")
        raise 