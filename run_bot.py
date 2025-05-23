"""
CoresAI Discord Bot Runner
"""

import asyncio
from src.discord_integration import start_bot

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}") 