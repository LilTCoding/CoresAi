"""
CoresAI Discord Bot Runner
"""

import asyncio
import logging
from src.discord_integration import start_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting CoresAI Discord Bot...")
        logger.info("This will create the following specialized channels:")
        logger.info("- 📊 Market Analysis: Real-time market data and technical analysis")
        logger.info("- 💹 Trading Room: Execute trades and manage positions")
        logger.info("- 🔔 Price Alerts: Set and monitor price alerts")
        logger.info("- 🧪 Strategy Lab: Create and test trading strategies")
        logger.info("- 🤖 AI Chat: Chat with CoresAI assistant")
        logger.info("- 📰 News Feed: Market news and updates")
        logger.info("- 📚 Learning Center: Trading education and resources")
        
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("\nBot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise 