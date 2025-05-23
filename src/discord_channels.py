"""
CoresAI Discord Channels Manager
Handles creation and management of specialized channels
"""

import discord
from discord.ext import commands
import logging
from typing import Dict, List, Optional
from .config import CATEGORY_ID

logger = logging.getLogger(__name__)

# Define channel structures with their descriptions and functions
CHANNEL_STRUCTURE = {
    'market-analysis': {
        'name': '📊-market-analysis',
        'description': 'Real-time market analysis and technical indicators',
        'detailed_description': (
            "Welcome to the Market Analysis channel! 📊\n\n"
            "This channel is your go-to destination for comprehensive market analysis, including:\n"
            "• Real-time technical indicators\n"
            "• Price trend analysis\n"
            "• Market sentiment tracking\n"
            "• Volume analysis\n"
            "• Support and resistance levels\n\n"
            "Use this channel to make informed trading decisions based on data-driven insights."
        ),
        'commands': [
            '!cores analyze <symbol> market - Get market overview',
            '!cores analyze <symbol> technical - Get technical analysis',
            '!cores analyze <symbol> sentiment - Get sentiment analysis'
        ],
        'topic': 'Market analysis channel - Get real-time market data, technical indicators, and price charts'
    },
    'trading-room': {
        'name': '💹-trading-room',
        'description': 'Execute trades and manage positions',
        'detailed_description': (
            "Welcome to the Trading Room! 💹\n\n"
            "This is your command center for all trading activities:\n"
            "• Execute buy/sell orders\n"
            "• Monitor active positions\n"
            "• Track portfolio performance\n"
            "• View trade history\n"
            "• Run trade simulations\n\n"
            "All your trading activities are securely logged and tracked here."
        ),
        'commands': [
            '!cores trade buy <symbol> <amount> [price] - Place buy order',
            '!cores trade sell <symbol> <amount> [price] - Place sell order',
            '!cores trade simulate <symbol> <amount> - Simulate trade',
            '!cores portfolio - View your portfolio'
        ],
        'topic': 'Trading channel - Execute trades, manage positions, and track your portfolio'
    },
    'price-alerts': {
        'name': '🔔-price-alerts',
        'description': 'Set and monitor price alerts',
        'detailed_description': (
            "Welcome to the Price Alerts channel! 🔔\n\n"
            "Stay on top of market movements with customizable alerts:\n"
            "• Set price threshold alerts\n"
            "• Monitor multiple assets simultaneously\n"
            "• Receive instant notifications\n"
            "• Track price breakouts\n"
            "• Set percentage change alerts\n\n"
            "Never miss an important price movement again!"
        ),
        'commands': [
            '!cores alert <symbol> <price> above - Alert when price goes above',
            '!cores alert <symbol> <price> below - Alert when price goes below',
            '!cores alerts list - List your active alerts',
            '!cores alert delete <id> - Delete an alert'
        ],
        'topic': 'Price alerts channel - Set and monitor price alerts for any symbol'
    },
    'strategy-lab': {
        'name': '🧪-strategy-lab',
        'description': 'Create and test trading strategies',
        'detailed_description': (
            "Welcome to the Strategy Lab! 🧪\n\n"
            "Your workspace for developing and testing trading strategies:\n"
            "• Create custom trading strategies\n"
            "• Backtest strategies with historical data\n"
            "• Optimize strategy parameters\n"
            "• Compare strategy performance\n"
            "• Export strategy results\n\n"
            "Turn your trading ideas into actionable strategies!"
        ),
        'commands': [
            '!cores strategy create <name> <params> - Create new strategy',
            '!cores strategy list - List your strategies',
            '!cores backtest <strategy> <symbol> [timeframe] - Run strategy backtest'
        ],
        'topic': 'Strategy laboratory - Create, test, and optimize trading strategies'
    },
    'ai-chat': {
        'name': '🤖-ai-chat',
        'description': 'Chat with CoresAI assistant',
        'detailed_description': (
            "Welcome to the AI Chat channel! 🤖\n\n"
            "Your personal AI trading assistant is here to help:\n"
            "• Get trading advice and insights\n"
            "• Learn about trading concepts\n"
            "• Analyze market conditions\n"
            "• Receive personalized recommendations\n"
            "• Access educational resources\n\n"
            "Ask anything about trading, and I'll be here to assist!"
        ),
        'commands': [
            '!cores chat <message> - Chat with AI',
            '!cores help - Get help with commands',
            '!cores explain <topic> - Get detailed explanations'
        ],
        'topic': 'AI chat channel - Get help, explanations, and chat with CoresAI'
    },
    'news-feed': {
        'name': '📰-news-feed',
        'description': 'Market news and updates',
        'detailed_description': (
            "Welcome to the News Feed! 📰\n\n"
            "Stay informed with real-time market news and updates:\n"
            "• Breaking market news\n"
            "• Economic calendar events\n"
            "• Company announcements\n"
            "• Market summaries\n"
            "• Industry updates\n\n"
            "All the market-moving news in one place!"
        ),
        'commands': [
            '!cores news <symbol> - Get latest news',
            '!cores summary <symbol> - Get market summary',
            '!cores calendar - Get economic calendar'
        ],
        'topic': 'News and updates channel - Stay informed with market news and events'
    },
    'learning-center': {
        'name': '📚-learning-center',
        'description': 'Trading education and resources',
        'detailed_description': (
            "Welcome to the Learning Center! 📚\n\n"
            "Your hub for trading education and resources:\n"
            "• Trading tutorials and guides\n"
            "• Technical analysis lessons\n"
            "• Risk management education\n"
            "• Trading psychology insights\n"
            "• Market terminology glossary\n\n"
            "Expand your trading knowledge and skills!"
        ),
        'commands': [
            '!cores learn <topic> - Get educational content',
            '!cores glossary <term> - Look up trading terms',
            '!cores guide <topic> - Get detailed guides'
        ],
        'topic': 'Learning center - Educational resources and trading guides'
    }
}

async def setup_channels(guild: discord.Guild) -> Dict[str, discord.TextChannel]:
    """Set up specialized channels in the CoresAI category"""
    try:
        # Get or create CoresAI category
        category = discord.utils.get(guild.categories, id=int(CATEGORY_ID))
        if not category:
            category = await guild.create_category('CoresAI')
            logger.info(f"Created CoresAI category")

        # Create channels
        channels = {}
        for channel_id, config in CHANNEL_STRUCTURE.items():
            # Check if channel exists
            channel = discord.utils.get(category.channels, name=config['name'])
            
            if not channel:
                # Create channel with proper permissions
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        read_message_history=True
                    ),
                    guild.me: discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_messages=True,
                        embed_links=True,
                        attach_files=True,
                        read_message_history=True,
                        manage_channels=True
                    )
                }
                
                channel = await category.create_text_channel(
                    name=config['name'],
                    topic=config['topic'],
                    overwrites=overwrites
                )
                
                # Send welcome message
                welcome_embed = discord.Embed(
                    title=f"Welcome to {config['name']}!",
                    description=config['detailed_description'],
                    color=discord.Color.blue()
                )
                
                welcome_embed.add_field(
                    name="Available Commands",
                    value="\n".join(config['commands']),
                    inline=False
                )

                # Add example usage field
                example_command = config['commands'][0].split(' - ')[0]
                welcome_embed.add_field(
                    name="Example Usage",
                    value=f"Try: `{example_command}`",
                    inline=False
                )
                
                await channel.send(embed=welcome_embed)
                logger.info(f"Created channel: {config['name']}")
            
            channels[channel_id] = channel

        return channels

    except Exception as e:
        logger.error(f"Error setting up channels: {e}")
        raise

class ChannelCommands(commands.Cog):
    """Channel-specific command handlers"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channels = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Set up channels when bot is ready"""
        try:
            for guild in self.bot.guilds:
                self.channels = await setup_channels(guild)
                logger.info(f"Channels set up for guild: {guild.name}")
        except Exception as e:
            logger.error(f"Error in on_ready: {e}")

    def get_channel(self, channel_id: str) -> Optional[discord.TextChannel]:
        """Get channel by ID"""
        return self.channels.get(channel_id)

    @commands.command(name='setup_channels')
    @commands.has_permissions(administrator=True)
    async def setup_channels_command(self, ctx: commands.Context):
        """Admin command to set up channels"""
        try:
            await ctx.send("Setting up CoresAI channels...")
            self.channels = await setup_channels(ctx.guild)
            await ctx.send("✅ Channels set up successfully!")
        except Exception as e:
            logger.error(f"Error in setup_channels_command: {e}")
            await ctx.send(f"❌ Error setting up channels: {str(e)}")

async def setup(bot: commands.Bot):
    """Add channel commands to bot"""
    await bot.add_cog(ChannelCommands(bot)) 