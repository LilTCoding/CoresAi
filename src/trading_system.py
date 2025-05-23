"""
CoresAI Trading System
Handles trade execution and position management
"""

import logging
from typing import Dict, Any, Optional, List
import asyncpg
import json
from datetime import datetime
import yfinance as yf
from .config import (
    DATABASE_URL,
    TRADING_ENABLED,
    SIMULATION_MODE,
    MAX_POSITION_SIZE,
    RISK_PERCENTAGE
)

logger = logging.getLogger(__name__)

class Position:
    def __init__(
        self,
        symbol: str,
        entry_price: float,
        amount: float,
        side: str,
        user_id: str
    ):
        self.symbol = symbol
        self.entry_price = entry_price
        self.amount = amount
        self.side = side
        self.user_id = user_id
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'entry_price': self.entry_price,
            'amount': self.amount,
            'side': self.side,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

async def get_db_connection() -> asyncpg.Connection:
    """Get database connection"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

async def get_current_price(symbol: str) -> float:
    """Get current market price"""
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info['regularMarketPrice']
    except Exception as e:
        logger.error(f"Error getting current price: {e}")
        raise

async def validate_trade(
    symbol: str,
    amount: float,
    price: Optional[float],
    user_id: str
) -> Dict[str, Any]:
    """Validate trade parameters"""
    try:
        # Check if trading is enabled
        if not TRADING_ENABLED and not SIMULATION_MODE:
            return {
                'valid': False,
                'reason': 'Trading is currently disabled'
            }

        # Get current price if not provided
        current_price = price or await get_current_price(symbol)
        
        # Calculate total value
        total_value = amount * current_price
        
        # Check position size limit
        if total_value > MAX_POSITION_SIZE:
            return {
                'valid': False,
                'reason': f'Position size exceeds maximum limit of ${MAX_POSITION_SIZE:,.2f}'
            }
        
        # Get user's current positions
        conn = await get_db_connection()
        positions = await conn.fetch(
            'SELECT * FROM positions WHERE user_id = $1',
            user_id
        )
        await conn.close()
        
        # Calculate total exposure
        total_exposure = sum(
            pos['amount'] * await get_current_price(pos['symbol'])
            for pos in positions
        )
        
        # Check risk percentage
        if total_exposure + total_value > MAX_POSITION_SIZE * (RISK_PERCENTAGE / 100):
            return {
                'valid': False,
                'reason': f'Total exposure would exceed risk limit of {RISK_PERCENTAGE}%'
            }
            
        return {
            'valid': True,
            'price': current_price,
            'total': total_value
        }
        
    except Exception as e:
        logger.error(f"Error validating trade: {e}")
        return {
            'valid': False,
            'reason': f'Validation error: {str(e)}'
        }

async def execute_trade(
    action: str,
    symbol: str,
    amount: float,
    price: Optional[float],
    user_id: str
) -> Dict[str, Any]:
    """Execute a trade"""
    try:
        # Validate trade
        validation = await validate_trade(symbol, amount, price, user_id)
        if not validation['valid']:
            return {
                'status': 'error',
                'details': validation['reason']
            }
            
        current_price = validation['price']
        total_value = validation['total']
        
        # Execute trade based on action
        if action == 'buy':
            position = Position(
                symbol=symbol,
                entry_price=current_price,
                amount=amount,
                side='long',
                user_id=user_id
            )
            
        elif action == 'sell':
            position = Position(
                symbol=symbol,
                entry_price=current_price,
                amount=amount,
                side='short',
                user_id=user_id
            )
            
        elif action == 'simulate':
            return {
                'status': 'simulated',
                'details': 'Trade simulation successful',
                'price': current_price,
                'total': total_value
            }
            
        else:
            return {
                'status': 'error',
                'details': f'Invalid action: {action}'
            }
            
        # Save position to database
        if not SIMULATION_MODE:
            conn = await get_db_connection()
            await conn.execute('''
                INSERT INTO positions (
                    symbol, entry_price, amount, side, user_id, timestamp
                ) VALUES ($1, $2, $3, $4, $5, $6)
            ''',
                position.symbol,
                position.entry_price,
                position.amount,
                position.side,
                position.user_id,
                position.timestamp
            )
            await conn.close()
            
        return {
            'status': 'success',
            'details': f'{action.title()} order executed successfully',
            'price': current_price,
            'total': total_value
        }
        
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return {
            'status': 'error',
            'details': f'Trade execution error: {str(e)}'
        }

async def get_positions(user_id: str) -> List[Dict[str, Any]]:
    """Get user's current positions"""
    try:
        conn = await get_db_connection()
        positions = await conn.fetch(
            'SELECT * FROM positions WHERE user_id = $1',
            user_id
        )
        await conn.close()
        
        # Calculate current values and P&L
        position_data = []
        for pos in positions:
            current_price = await get_current_price(pos['symbol'])
            entry_value = pos['amount'] * pos['entry_price']
            current_value = pos['amount'] * current_price
            pnl = current_value - entry_value
            pnl_percentage = (pnl / entry_value) * 100
            
            position_data.append({
                'symbol': pos['symbol'],
                'side': pos['side'],
                'amount': pos['amount'],
                'entry_price': pos['entry_price'],
                'current_price': current_price,
                'pnl': pnl,
                'pnl_percentage': pnl_percentage,
                'timestamp': pos['timestamp'].isoformat()
            })
            
        return position_data
        
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise

async def close_position(
    position_id: int,
    user_id: str
) -> Dict[str, Any]:
    """Close a trading position"""
    try:
        conn = await get_db_connection()
        
        # Get position
        position = await conn.fetchrow(
            'SELECT * FROM positions WHERE id = $1 AND user_id = $2',
            position_id, user_id
        )
        
        if not position:
            return {
                'status': 'error',
                'details': 'Position not found'
            }
            
        # Get current price
        current_price = await get_current_price(position['symbol'])
        
        # Calculate P&L
        entry_value = position['amount'] * position['entry_price']
        close_value = position['amount'] * current_price
        pnl = close_value - entry_value if position['side'] == 'long' else entry_value - close_value
        
        # Delete position
        await conn.execute(
            'DELETE FROM positions WHERE id = $1',
            position_id
        )
        
        await conn.close()
        
        return {
            'status': 'success',
            'details': 'Position closed successfully',
            'pnl': pnl,
            'close_price': current_price
        }
        
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        return {
            'status': 'error',
            'details': f'Error closing position: {str(e)}'
        }

async def get_trade_history(user_id: str) -> Dict[str, Any]:
    """Get user's trade history"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/trade/history",
                params={"user_id": user_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error fetching trade history: {e}")
        raise

async def cancel_order(order_id: str, user_id: str) -> Dict[str, Any]:
    """Cancel a pending trade order"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/trade/cancel",
                json={"order_id": order_id, "user_id": user_id}
            ) as response:
                if response.status == 200:
                    return {
                        "status": "success",
                        "details": "Order cancelled successfully"
                    }
                else:
                    error_data = await response.text()
                    return {
                        "status": "error",
                        "details": f"Failed to cancel order: {error_data}"
                    }

    except Exception as e:
        logger.error(f"Error in cancel_order: {e}")
        return {
            "status": "error",
            "details": f"Order cancellation failed: {str(e)}"
        }

async def get_order_status(order_id: str, user_id: str) -> Dict[str, Any]:
    """Get status of a specific order"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/trade/status",
                params={"order_id": order_id, "user_id": user_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error fetching order status: {e}")
        raise 