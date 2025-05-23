"""
CoresAI Backtesting Module
Handles strategy backtesting and performance analysis
"""

import logging
from typing import Dict, Any
import aiohttp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
from .config import API_URL

logger = logging.getLogger(__name__)

async def run_backtest(
    strategy_name: str,
    symbol: str,
    timeframe: str,
    user_id: str
) -> Dict[str, Any]:
    """Run strategy backtesting"""
    try:
        # Get strategy details
        strategy = await get_strategy_details(strategy_name, user_id)
        
        # Get historical data
        data = await fetch_historical_data(symbol, timeframe)
        
        # Run backtest simulation
        results = await simulate_strategy(
            strategy=strategy,
            data=data,
            user_id=user_id
        )
        
        # Calculate performance metrics
        metrics = calculate_performance_metrics(results)
        
        # Generate performance chart
        chart_path = generate_performance_chart(results, symbol, strategy_name)
        
        # Combine results
        return {
            **metrics,
            "chart_path": chart_path,
            "strategy_name": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe
        }

    except Exception as e:
        logger.error(f"Error in run_backtest: {e}")
        raise

async def get_strategy_details(strategy_name: str, user_id: str) -> Dict[str, Any]:
    """Get strategy configuration"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/strategy/details",
                params={"strategy_name": strategy_name, "user_id": user_id}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error fetching strategy details: {e}")
        raise

async def fetch_historical_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """Fetch historical market data"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/api/market/historical",
                params={"symbol": symbol, "timeframe": timeframe}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return pd.DataFrame(data["data"])
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise

async def simulate_strategy(
    strategy: Dict[str, Any],
    data: pd.DataFrame,
    user_id: str
) -> Dict[str, Any]:
    """Simulate strategy performance"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_URL}/api/backtest/simulate",
                json={
                    "strategy": strategy,
                    "data": data.to_dict(orient="records"),
                    "user_id": user_id
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API error: {await response.text()}")

    except Exception as e:
        logger.error(f"Error in strategy simulation: {e}")
        raise

def calculate_performance_metrics(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate strategy performance metrics"""
    try:
        # Extract performance data
        equity_curve = pd.Series(results["equity_curve"])
        trades = results["trades"]
        
        # Calculate returns
        returns = equity_curve.pct_change().dropna()
        
        # Calculate metrics
        total_return = ((equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1) * 100
        sharpe_ratio = calculate_sharpe_ratio(returns)
        max_drawdown = calculate_max_drawdown(equity_curve)
        
        # Calculate trade statistics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t["profit"] > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate profit factor
        gross_profit = sum([t["profit"] for t in trades if t["profit"] > 0])
        gross_loss = abs(sum([t["profit"] for t in trades if t["profit"] < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
        
        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "total_trades": total_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor
        }

    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}")
        raise

def calculate_sharpe_ratio(returns: pd.Series) -> float:
    """Calculate Sharpe ratio"""
    if len(returns) < 2:
        return 0
    
    # Assuming risk-free rate of 0% for simplicity
    return np.sqrt(252) * (returns.mean() / returns.std())

def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """Calculate maximum drawdown percentage"""
    rolling_max = equity_curve.expanding().max()
    drawdowns = (equity_curve - rolling_max) / rolling_max * 100
    return abs(drawdowns.min())

def generate_performance_chart(
    results: Dict[str, Any],
    symbol: str,
    strategy_name: str
) -> str:
    """Generate performance visualization chart"""
    try:
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
        
        # Plot equity curve
        equity_data = pd.Series(results["equity_curve"])
        ax1.plot(equity_data.index, equity_data.values, label="Portfolio Value")
        ax1.set_title(f"{strategy_name} Performance on {symbol}")
        ax1.set_xlabel("Trade Number")
        ax1.set_ylabel("Portfolio Value")
        ax1.grid(True)
        ax1.legend()
        
        # Plot drawdown
        rolling_max = equity_data.expanding().max()
        drawdowns = (equity_data - rolling_max) / rolling_max * 100
        ax2.fill_between(drawdowns.index, drawdowns.values, 0, color='red', alpha=0.3)
        ax2.set_xlabel("Trade Number")
        ax2.set_ylabel("Drawdown %")
        ax2.grid(True)
        
        # Save chart
        os.makedirs("charts", exist_ok=True)
        chart_path = f"charts/{symbol}_{strategy_name}_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path

    except Exception as e:
        logger.error(f"Error generating performance chart: {e}")
        raise 