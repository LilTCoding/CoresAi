"""
CoresAI Discord Integration
Handles Discord bot and OAuth functionality
"""

import discord
from discord.ext import commands
import logging
from .config import (
    DISCORD_BOT_TOKEN,
    GUILD_ID,
    CATEGORY_ID,
    UPDATES_CHANNEL_ID,
    LOGS_CHANNEL_ID
)
from .discord_commands import AICoreCommands

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoresAIBot(commands.Bot):
    """CoresAI Discord Bot"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix="!cores ",
            intents=intents,
            help_command=None
        )
        
        # Store channel references
        self.updates_channel = None
        self.logs_channel = None
        
    async def setup_hook(self):
        """Setup bot hooks and commands"""
        try:
            # Load command cogs
            await self.add_cog(AICoreCommands(self))
            
            # Sync commands with Discord
            logger.info("Syncing commands with Discord...")
            await self.tree.sync()
            
        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")
            raise
    
    async def on_ready(self):
        """Called when bot is ready"""
        try:
            logger.info(f"Logged in as {self.user.name}")
            
            # Get channel references
            guild = self.get_guild(int(GUILD_ID))
            if guild:
                self.updates_channel = guild.get_channel(int(UPDATES_CHANNEL_ID))
                self.logs_channel = guild.get_channel(int(LOGS_CHANNEL_ID))
                
                if self.updates_channel and self.logs_channel:
                    await self.updates_channel.send("🟢 CoresAI Bot is now online!")
                else:
                    logger.error("Could not find required channels")
            else:
                logger.error("Could not find guild")
            
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        try:
            if isinstance(error, commands.errors.CommandNotFound):
                await ctx.send("Command not found. Use `!cores help` to see available commands.")
            else:
                logger.error(f"Command error: {error}")
                await ctx.send(f"An error occurred: {str(error)}")
                
                if self.logs_channel:
                    await self.logs_channel.send(
                        f"⚠️ Command Error:\n"
                        f"User: {ctx.author}\n"
                        f"Command: {ctx.message.content}\n"
                        f"Error: {str(error)}"
                    )
                    
        except Exception as e:
            logger.error(f"Error handling command error: {e}")
    
    async def log_event(self, event_type: str, details: str):
        """Log events to Discord channel"""
        try:
            if self.logs_channel:
                await self.logs_channel.send(
                    f"📝 {event_type}:\n{details}"
                )
        except Exception as e:
            logger.error(f"Error logging event: {e}")

def create_bot() -> CoresAIBot:
    """Create and configure the Discord bot"""
    return CoresAIBot()

async def start_bot():
    """Start the Discord bot"""
    try:
        bot = create_bot()
        await bot.start(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise 