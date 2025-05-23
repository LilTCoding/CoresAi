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
from .discord_channels import ChannelCommands, CHANNEL_STRUCTURE

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
        self.specialized_channels = {}
        
    async def setup_hook(self):
        """Setup bot hooks and commands"""
        try:
            # Load command cogs
            await self.add_cog(AICoreCommands(self))
            await self.add_cog(ChannelCommands(self))
            
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
            
            # Get guild and channel references
            guild = self.get_guild(int(GUILD_ID))
            if guild:
                self.updates_channel = guild.get_channel(int(UPDATES_CHANNEL_ID))
                self.logs_channel = guild.get_channel(int(LOGS_CHANNEL_ID))
                
                if self.updates_channel and self.logs_channel:
                    await self.updates_channel.send("🟢 CoresAI Bot is now online!")
                    
                    # Send status update to each specialized channel
                    channel_cog = self.get_cog('ChannelCommands')
                    if channel_cog:
                        for channel_id, channel in channel_cog.channels.items():
                            if channel:
                                embed = discord.Embed(
                                    title="🟢 CoresAI Bot Online",
                                    description=f"Ready to process {CHANNEL_STRUCTURE[channel_id]['description'].lower()}",
                                    color=discord.Color.green()
                                )
                                await channel.send(embed=embed)
                else:
                    logger.error("Could not find required channels")
            else:
                logger.error("Could not find guild")
            
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")
    
    async def on_message(self, message: discord.Message):
        """Handle message events"""
        try:
            # Ignore messages from the bot itself
            if message.author == self.user:
                return

            # Process commands
            await self.process_commands(message)
            
            # Route messages to appropriate handlers based on channel
            if message.channel.category_id == int(CATEGORY_ID):
                channel_name = message.channel.name
                
                # Find matching channel configuration
                for channel_id, config in CHANNEL_STRUCTURE.items():
                    if config['name'] == channel_name:
                        # Handle channel-specific functionality
                        await self.handle_channel_message(message, channel_id, config)
                        break
            
        except Exception as e:
            logger.error(f"Error in on_message: {e}")
            await self.log_error(f"Message processing error: {str(e)}")
    
    async def handle_channel_message(
        self,
        message: discord.Message,
        channel_id: str,
        config: dict
    ):
        """Handle messages in specialized channels"""
        try:
            # Check if message starts with command prefix
            if not message.content.startswith(self.command_prefix):
                # Send help message for non-command messages
                embed = discord.Embed(
                    title="Available Commands",
                    description="\n".join(config['commands']),
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
                return
            
            # Process channel-specific commands
            command = message.content[len(self.command_prefix):].split()[0]
            
            # Check if command is valid for this channel
            valid_command = False
            for cmd in config['commands']:
                if cmd.split()[0] == command:
                    valid_command = True
                    break
            
            if not valid_command:
                await message.channel.send(
                    f"❌ This command is not available in the {config['name']} channel.\n"
                    f"Please use one of the following commands:\n"
                    f"```\n{chr(10).join(config['commands'])}\n```"
                )
            
        except Exception as e:
            logger.error(f"Error handling channel message: {e}")
            await self.log_error(f"Channel message handling error: {str(e)}")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        try:
            if isinstance(error, commands.errors.CommandNotFound):
                # Check if we're in a specialized channel
                if ctx.channel.category_id == int(CATEGORY_ID):
                    for config in CHANNEL_STRUCTURE.values():
                        if config['name'] == ctx.channel.name:
                            await ctx.send(
                                f"Command not found. Available commands in this channel:\n"
                                f"```\n{chr(10).join(config['commands'])}\n```"
                            )
                            return
                
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
            
    async def log_error(self, error: str):
        """Log errors to Discord channel"""
        try:
            if self.logs_channel:
                await self.logs_channel.send(
                    f"⚠️ Error:\n{error}"
                )
        except Exception as e:
            logger.error(f"Error logging error: {e}")

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