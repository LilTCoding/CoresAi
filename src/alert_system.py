"""
CoresAI Alert System
Handles price alerts and notifications
"""

import logging
from typing import Dict, Any, List, Optional
import asyncpg
import asyncio
from datetime import datetime
import yfinance as yf
from .config import (
    DATABASE_URL,
    MAX_ALERTS_PER_USER,
    ALERT_CHECK_INTERVAL
)

logger = logging.getLogger(__name__)

class PriceAlert:
    def __init__(
        self,
        symbol: str,
        target_price: float,
        condition: str,
        user_id: str,
        channel_id: Optional[str] = None
    ):
        self.symbol = symbol
        self.target_price = target_price
        self.condition = condition  # 'above' or 'below'
        self.user_id = user_id
        self.channel_id = channel_id
        self.timestamp = datetime.now()
        self.triggered = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'target_price': self.target_price,
            'condition': self.condition,
            'user_id': self.user_id,
            'channel_id': self.channel_id,
            'timestamp': self.timestamp.isoformat(),
            'triggered': self.triggered
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceAlert':
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

async def create_alert(
    symbol: str,
    target_price: float,
    condition: str,
    user_id: str,
    channel_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new price alert"""
    try:
        # Validate condition
        if condition not in ['above', 'below']:
            return {
                'status': 'error',
                'details': 'Invalid condition. Must be "above" or "below".'
            }

        # Check user's alert count
        conn = await get_db_connection()
        alert_count = await conn.fetchval(
            'SELECT COUNT(*) FROM alerts WHERE user_id = $1',
            user_id
        )

        if alert_count >= MAX_ALERTS_PER_USER:
            await conn.close()
            return {
                'status': 'error',
                'details': f'Maximum number of alerts ({MAX_ALERTS_PER_USER}) reached'
            }

        # Create alert
        alert = PriceAlert(
            symbol=symbol,
            target_price=target_price,
            condition=condition,
            user_id=user_id,
            channel_id=channel_id
        )

        # Save to database
        await conn.execute('''
            INSERT INTO alerts (
                symbol, target_price, condition, user_id,
                channel_id, timestamp, triggered
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ''',
            alert.symbol,
            alert.target_price,
            alert.condition,
            alert.user_id,
            alert.channel_id,
            alert.timestamp,
            alert.triggered
        )

        await conn.close()

        return {
            'status': 'success',
            'details': 'Alert created successfully',
            'alert': alert.to_dict()
        }

    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return {
            'status': 'error',
            'details': f'Failed to create alert: {str(e)}'
        }

async def get_alerts(user_id: str) -> List[Dict[str, Any]]:
    """Get user's active alerts"""
    try:
        conn = await get_db_connection()
        alerts = await conn.fetch(
            'SELECT * FROM alerts WHERE user_id = $1 AND triggered = FALSE',
            user_id
        )
        await conn.close()

        return [dict(alert) for alert in alerts]

    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise

async def delete_alert(alert_id: int, user_id: str) -> Dict[str, Any]:
    """Delete a price alert"""
    try:
        conn = await get_db_connection()
        result = await conn.execute(
            'DELETE FROM alerts WHERE id = $1 AND user_id = $2',
            alert_id, user_id
        )
        await conn.close()

        if result == 'DELETE 1':
            return {
                'status': 'success',
                'details': 'Alert deleted successfully'
            }
        else:
            return {
                'status': 'error',
                'details': 'Alert not found'
            }

    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        return {
            'status': 'error',
            'details': f'Failed to delete alert: {str(e)}'
        }

async def check_price_alerts(bot) -> None:
    """Check and trigger price alerts"""
    try:
        while True:
            conn = await get_db_connection()
            alerts = await conn.fetch(
                'SELECT * FROM alerts WHERE triggered = FALSE'
            )

            for alert in alerts:
                try:
                    # Get current price
                    ticker = yf.Ticker(alert['symbol'])
                    current_price = ticker.info['regularMarketPrice']

                    # Check if alert should be triggered
                    should_trigger = (
                        (alert['condition'] == 'above' and current_price >= alert['target_price']) or
                        (alert['condition'] == 'below' and current_price <= alert['target_price'])
                    )

                    if should_trigger:
                        # Mark alert as triggered
                        await conn.execute(
                            'UPDATE alerts SET triggered = TRUE WHERE id = $1',
                            alert['id']
                        )

                        # Send notification
                        if alert['channel_id']:
                            channel = bot.get_channel(int(alert['channel_id']))
                            if channel:
                                await channel.send(
                                    f"🔔 Price Alert for {alert['symbol']}!\n"
                                    f"Target: ${alert['target_price']:.2f} ({alert['condition']})\n"
                                    f"Current: ${current_price:.2f}"
                                )

                except Exception as e:
                    logger.error(f"Error checking alert {alert['id']}: {e}")
                    continue

            await conn.close()
            await asyncio.sleep(ALERT_CHECK_INTERVAL)

    except Exception as e:
        logger.error(f"Error in check_price_alerts: {e}")
        # Wait before retrying
        await asyncio.sleep(60)
        asyncio.create_task(check_price_alerts(bot))

async def start_alert_system(bot) -> None:
    """Start the alert system"""
    try:
        # Create alerts table if not exists
        conn = await get_db_connection()
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                target_price FLOAT NOT NULL,
                condition TEXT NOT NULL,
                user_id TEXT NOT NULL,
                channel_id TEXT,
                timestamp TIMESTAMP NOT NULL,
                triggered BOOLEAN DEFAULT FALSE
            )
        ''')
        await conn.close()

        # Start alert checker
        asyncio.create_task(check_price_alerts(bot))

    except Exception as e:
        logger.error(f"Error starting alert system: {e}")
        raise 