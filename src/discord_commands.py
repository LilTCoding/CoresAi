"""
CoresAI Discord Commands
Implements AI functionality as Discord commands
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
from datetime import datetime
from typing import Optional, List
import logging

from .config import (
    GUILD_ID,
    CATEGORY_ID,
    UPDATES_CHANNEL_ID,
    LOGS_CHANNEL_ID,
    OWNER_ID
)

logger = logging.getLogger(__name__)

class AICoreCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.processing_users = set()
        self.conversation_history = {}

    @app_commands.command(name="chat", description="Chat with CoresAI")
    async def chat(self, interaction: discord.Interaction, message: str):
        """Chat with CoresAI"""
        try:
            # Defer reply since AI processing might take time
            await interaction.response.defer()

            user_id = str(interaction.user.id)
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []

            # Add user message to history
            self.conversation_history[user_id].append({
                "role": "user",
                "content": message
            })

            # Process with AI
            from .ai_processing import process_chat_message
            response = await process_chat_message(message, self.conversation_history[user_id])

            # Add AI response to history
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": response
            })

            # Create embed for response
            embed = discord.Embed(
                title="CoresAI Response",
                description=response,
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in chat command: {e}")
            await interaction.followup.send(
                "Sorry, I encountered an error processing your message.",
                ephemeral=True
            )

    @app_commands.command(name="analyze", description="Analyze market data or trading patterns")
    @app_commands.choices(analysis_type=[
        app_commands.Choice(name="Market Analysis", value="market"),
        app_commands.Choice(name="Technical Analysis", value="technical"),
        app_commands.Choice(name="Sentiment Analysis", value="sentiment")
    ])
    async def analyze(
        self,
        interaction: discord.Interaction,
        analysis_type: str,
        symbol: str,
        timeframe: Optional[str] = "1d"
    ):
        """Analyze market data"""
        try:
            await interaction.response.defer()

            # Process analysis request
            from .market_analysis import analyze_market_data
            analysis_result = await analyze_market_data(
                symbol=symbol,
                analysis_type=analysis_type,
                timeframe=timeframe
            )

            # Create embed with analysis results
            embed = discord.Embed(
                title=f"{symbol} Analysis",
                description="Market analysis results",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )

            for key, value in analysis_result.items():
                embed.add_field(
                    name=key.replace("_", " ").title(),
                    value=value,
                    inline=False
                )

            # Add chart if available
            if analysis_result.get("chart_path"):
                file = discord.File(
                    analysis_result["chart_path"],
                    filename="analysis.png"
                )
                embed.set_image(url="attachment://analysis.png")
                await interaction.followup.send(embed=embed, file=file)
            else:
                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await interaction.followup.send(
                "Sorry, I encountered an error during analysis.",
                ephemeral=True
            )

    @app_commands.command(name="trade", description="Execute or simulate trades")
    @app_commands.choices(action=[
        app_commands.Choice(name="Buy", value="buy"),
        app_commands.Choice(name="Sell", value="sell"),
        app_commands.Choice(name="Simulate", value="simulate")
    ])
    async def trade(
        self,
        interaction: discord.Interaction,
        action: str,
        symbol: str,
        amount: float,
        price: Optional[float] = None
    ):
        """Execute trading operations"""
        try:
            await interaction.response.defer()

            # Check if user is authorized
            if not await self.is_user_authorized(interaction.user.id):
                await interaction.followup.send(
                    "You are not authorized to execute trades. Please link your account first.",
                    ephemeral=True
                )
                return

            # Process trade
            from .trading_system import execute_trade
            trade_result = await execute_trade(
                action=action,
                symbol=symbol,
                amount=amount,
                price=price,
                user_id=str(interaction.user.id)
            )

            # Create embed with trade results
            embed = discord.Embed(
                title="Trade Execution",
                description=f"{action.title()} order for {symbol}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )

            embed.add_field(
                name="Status",
                value=trade_result["status"],
                inline=False
            )
            embed.add_field(
                name="Details",
                value=trade_result["details"],
                inline=False
            )
            if trade_result.get("price"):
                embed.add_field(
                    name="Price",
                    value=f"${trade_result['price']:.2f}",
                    inline=True
                )
            if trade_result.get("total"):
                embed.add_field(
                    name="Total",
                    value=f"${trade_result['total']:.2f}",
                    inline=True
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in trade command: {e}")
            await interaction.followup.send(
                "Sorry, I encountered an error processing your trade.",
                ephemeral=True
            )

    @app_commands.command(name="portfolio", description="View your trading portfolio")
    async def portfolio(self, interaction: discord.Interaction):
        """View portfolio status"""
        try:
            await interaction.response.defer()

            # Get portfolio data
            from .portfolio_manager import get_portfolio
            portfolio_data = await get_portfolio(str(interaction.user.id))

            # Create embed with portfolio information
            embed = discord.Embed(
                title="Trading Portfolio",
                description="Your current portfolio status",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )

            # Add balance information
            embed.add_field(
                name="Total Balance",
                value=f"${portfolio_data['total_balance']:.2f}",
                inline=False
            )
            embed.add_field(
                name="Available Cash",
                value=f"${portfolio_data['available_cash']:.2f}",
                inline=True
            )
            embed.add_field(
                name="Invested Amount",
                value=f"${portfolio_data['invested_amount']:.2f}",
                inline=True
            )

            # Add holdings
            holdings_text = ""
            for holding in portfolio_data['holdings']:
                holdings_text += f"**{holding['symbol']}**: {holding['quantity']} shares @ ${holding['avg_price']:.2f}\n"
            
            if holdings_text:
                embed.add_field(
                    name="Holdings",
                    value=holdings_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="Holdings",
                    value="No current holdings",
                    inline=False
                )

            # Add performance metrics
            embed.add_field(
                name="Daily P/L",
                value=f"${portfolio_data['daily_pl']:.2f} ({portfolio_data['daily_pl_percent']:.2f}%)",
                inline=True
            )
            embed.add_field(
                name="Total P/L",
                value=f"${portfolio_data['total_pl']:.2f} ({portfolio_data['total_pl_percent']:.2f}%)",
                inline=True
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in portfolio command: {e}")
            await interaction.followup.send(
                "Sorry, I encountered an error fetching your portfolio.",
                ephemeral=True
            )

    @app_commands.command(name="alert", description="Set up price alerts")
    @app_commands.choices(condition=[
        app_commands.Choice(name="Above", value="above"),
        app_commands.Choice(name="Below", value="below")
    ])
    async def alert(
        self,
        interaction: discord.Interaction,
        symbol: str,
        price: float,
        condition: str
    ):
        """Set up price alerts"""
        try:
            await interaction.response.defer()

            # Set up alert
            from .alert_system import create_alert
            alert_id = await create_alert(
                user_id=str(interaction.user.id),
                symbol=symbol,
                price=price,
                condition=condition
            )

            embed = discord.Embed(
                title="Price Alert Created",
                description=f"Alert for {symbol}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )

            embed.add_field(
                name="Condition",
                value=f"Price {condition} ${price:.2f}",
                inline=False
            )
            embed.add_field(
                name="Alert ID",
                value=alert_id,
                inline=False
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in alert command: {e}")
            await interaction.followup.send(
                "Sorry, I encountered an error setting up the alert.",
                ephemeral=True
            )

    @app_commands.command(name="strategy", description="Create or manage trading strategies")
    @app_commands.choices(action=[
        app_commands.Choice(name="Create", value="create"),
        app_commands.Choice(name="List", value="list"),
        app_commands.Choice(name="Delete", value="delete")
    ])
    async def strategy(
        self,
        interaction: discord.Interaction,
        action: str,
        name: Optional[str] = None,
        parameters: Optional[str] = None
    ):
        """Manage trading strategies"""
        try:
            await interaction.response.defer()

            from .strategy_manager import manage_strategy
            result = await manage_strategy(
                action=action,
                user_id=str(interaction.user.id),
                name=name,
                parameters=parameters
            )

            embed = discord.Embed(
                title="Strategy Management",
                description=f"Action: {action.title()}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )

            if action == "list":
                strategies_text = ""
                for strategy in result["strategies"]:
                    strategies_text += f"**{strategy['name']}**\n{strategy['description']}\n\n"
                embed.add_field(
                    name="Available Strategies",
                    value=strategies_text or "No strategies found",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Result",
                    value=result["message"],
                    inline=False
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in strategy command: {e}")
            await interaction.followup.send(
                "Sorry, I encountered an error managing strategies.",
                ephemeral=True
            )

    @app_commands.command(name="backtest", description="Run strategy backtesting")
    async def backtest(
        self,
        interaction: discord.Interaction,
        strategy_name: str,
        symbol: str,
        timeframe: str = "1y"
    ):
        """Run strategy backtesting"""
        try:
            await interaction.response.defer()

            from .backtesting import run_backtest
            results = await run_backtest(
                strategy_name=strategy_name,
                symbol=symbol,
                timeframe=timeframe,
                user_id=str(interaction.user.id)
            )

            embed = discord.Embed(
                title="Backtest Results",
                description=f"Strategy: {strategy_name} on {symbol}",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )

            # Add performance metrics
            embed.add_field(
                name="Total Return",
                value=f"{results['total_return']:.2f}%",
                inline=True
            )
            embed.add_field(
                name="Sharpe Ratio",
                value=f"{results['sharpe_ratio']:.2f}",
                inline=True
            )
            embed.add_field(
                name="Max Drawdown",
                value=f"{results['max_drawdown']:.2f}%",
                inline=True
            )

            # Add trade statistics
            embed.add_field(
                name="Total Trades",
                value=results['total_trades'],
                inline=True
            )
            embed.add_field(
                name="Win Rate",
                value=f"{results['win_rate']:.2f}%",
                inline=True
            )
            embed.add_field(
                name="Profit Factor",
                value=f"{results['profit_factor']:.2f}",
                inline=True
            )

            # Add performance chart
            if results.get("chart_path"):
                file = discord.File(
                    results["chart_path"],
                    filename="backtest.png"
                )
                embed.set_image(url="attachment://backtest.png")
                await interaction.followup.send(embed=embed, file=file)
            else:
                await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in backtest command: {e}")
            await interaction.followup.send(
                "Sorry, I encountered an error running the backtest.",
                ephemeral=True
            )

    async def is_user_authorized(self, user_id: int) -> bool:
        """Check if user is authorized for trading"""
        # Add your authorization logic here
        return True  # Temporary return for testing

async def setup(bot: commands.Bot):
    """Add the cog to the bot"""
    await bot.add_cog(AICoreCommands(bot)) 