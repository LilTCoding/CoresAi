"""
CoresAI Database Initialization Script
Creates necessary database tables and indexes
"""

import asyncio
import asyncpg
import logging
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from src.config import DATABASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """Initialize database tables"""
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Connected to database")

        # Create positions table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                entry_price FLOAT NOT NULL,
                amount FLOAT NOT NULL,
                side TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_positions_user_id ON positions(user_id);
            CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
        ''')
        logger.info("Created positions table")

        # Create alerts table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                symbol TEXT NOT NULL,
                target_price FLOAT NOT NULL,
                condition TEXT NOT NULL,
                user_id TEXT NOT NULL,
                channel_id TEXT,
                timestamp TIMESTAMP NOT NULL,
                triggered BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
            CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol);
            CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered);
        ''')
        logger.info("Created alerts table")

        # Create strategies table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS strategies (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                parameters JSONB NOT NULL,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, user_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON strategies(user_id);
            CREATE INDEX IF NOT EXISTS idx_strategies_active ON strategies(active);
        ''')
        logger.info("Created strategies table")

        # Create backtests table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS backtests (
                id SERIAL PRIMARY KEY,
                strategy_id INTEGER REFERENCES strategies(id),
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                results JSONB NOT NULL,
                metrics JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_backtests_strategy_id ON backtests(strategy_id);
            CREATE INDEX IF NOT EXISTS idx_backtests_symbol ON backtests(symbol);
        ''')
        logger.info("Created backtests table")

        # Create trades table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                position_id INTEGER REFERENCES positions(id),
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                amount FLOAT NOT NULL,
                price FLOAT NOT NULL,
                total FLOAT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_trades_position_id ON trades(position_id);
            CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
            CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
        ''')
        logger.info("Created trades table")

        await conn.close()
        logger.info("Database initialization completed successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except KeyboardInterrupt:
        logger.info("Database initialization interrupted by user")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1) 