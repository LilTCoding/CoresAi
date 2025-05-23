"""
CoresAI Market Analysis Module
Handles market data analysis and visualization
"""

import logging
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, Any, Optional
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from .config import MARKET_DATA_PROVIDER, MARKET_DATA_API_KEY

logger = logging.getLogger(__name__)

def get_timeframe_delta(timeframe: str) -> timedelta:
    """Convert timeframe string to timedelta"""
    units = {
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks',
        'mo': 'months',
        'y': 'years'
    }
    
    amount = int(''.join(filter(str.isdigit, timeframe)))
    unit = ''.join(filter(str.isalpha, timeframe)).lower()
    
    if unit == 'mo':
        return timedelta(days=amount * 30)
    
    return timedelta(**{units[unit]: amount})

async def get_market_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """Fetch market data from provider"""
    try:
        end_date = datetime.now()
        start_date = end_date - get_timeframe_delta(timeframe)
        
        if MARKET_DATA_PROVIDER == 'yahoo':
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval='1d')
            return df
        else:
            raise ValueError(f"Unsupported market data provider: {MARKET_DATA_PROVIDER}")
            
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise

def calculate_technical_indicators(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate technical indicators"""
    try:
        # Calculate moving averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Get latest values
        latest = df.iloc[-1]
        return {
            'close': latest['Close'],
            'sma_20': latest['SMA_20'],
            'sma_50': latest['SMA_50'],
            'rsi': latest['RSI'],
            'macd': latest['MACD'],
            'macd_signal': latest['Signal_Line'],
            'volume': latest['Volume']
        }
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        raise

def generate_chart(df: pd.DataFrame, symbol: str) -> str:
    """Generate interactive chart"""
    try:
        fig = go.Figure()
        
        # Add candlestick chart
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ))
        
        # Add moving averages
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_20'],
            name='SMA 20',
            line=dict(color='orange')
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_50'],
            name='SMA 50',
            line=dict(color='blue')
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} Price Chart',
            yaxis_title='Price',
            xaxis_title='Date',
            template='plotly_dark'
        )
        
        # Save chart
        os.makedirs('data/charts', exist_ok=True)
        chart_path = f'data/charts/{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        fig.write_image(chart_path)
        
        return chart_path
        
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        raise

async def analyze_market_data(
    symbol: str,
    analysis_type: str,
    timeframe: str
) -> Dict[str, Any]:
    """Analyze market data based on specified type"""
    try:
        # Fetch market data
        df = await get_market_data(symbol, timeframe)
        
        # Calculate indicators
        indicators = calculate_technical_indicators(df)
        
        # Generate chart
        chart_path = generate_chart(df, symbol)
        
        # Prepare analysis results based on type
        if analysis_type == 'market':
            return {
                'current_price': f"${indicators['close']:.2f}",
                'volume': f"{indicators['volume']:,.0f}",
                'price_change': f"{((df['Close'][-1] / df['Close'][0] - 1) * 100):.2f}%",
                'chart_path': chart_path
            }
            
        elif analysis_type == 'technical':
            # Add technical analysis signals
            sma_signal = "Bullish" if indicators['sma_20'] > indicators['sma_50'] else "Bearish"
            rsi_signal = "Overbought" if indicators['rsi'] > 70 else "Oversold" if indicators['rsi'] < 30 else "Neutral"
            macd_signal = "Bullish" if indicators['macd'] > indicators['macd_signal'] else "Bearish"
            
            return {
                'sma_signal': sma_signal,
                'rsi_value': f"{indicators['rsi']:.2f}",
                'rsi_signal': rsi_signal,
                'macd_signal': macd_signal,
                'chart_path': chart_path
            }
            
        elif analysis_type == 'sentiment':
            # TODO: Implement sentiment analysis
            return {
                'sentiment': "Neutral",
                'confidence': "Medium",
                'chart_path': chart_path
            }
            
        else:
            raise ValueError(f"Invalid analysis type: {analysis_type}")
            
    except Exception as e:
        logger.error(f"Error in analyze_market_data: {e}")
        raise 