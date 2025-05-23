#!/usr/bin/env python3
"""
CoresAI Crypto Trading Backend
Advanced crypto trading and social analytics API with security features
"""

import asyncio
import json
import logging
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from decimal import Decimal
import os

from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import httpx
import aioredis
from web3 import Web3
import ccxt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CoresAI Crypto Trading API",
    description="Advanced crypto trading and social analytics with AI insights",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/YOUR_PROJECT_ID")
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")

# Web3 connection
w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))

# Data Models
class WalletConnectionRequest(BaseModel):
    address: str = Field(..., description="Wallet address to connect")
    signature: str = Field(..., description="Signature for verification")
    message: str = Field(..., description="Message that was signed")

class TradeRequest(BaseModel):
    token_in: str = Field(..., description="Token to sell")
    token_out: str = Field(..., description="Token to buy")
    amount_in: float = Field(..., description="Amount to trade")
    slippage: float = Field(default=0.5, description="Slippage tolerance")
    wallet_address: str = Field(..., description="Wallet address")

class FriendWalletRequest(BaseModel):
    wallet_address: str = Field(..., description="Friend's wallet address")
    alias: Optional[str] = Field(None, description="Optional alias for the wallet")

class PriceAlertRequest(BaseModel):
    token: str = Field(..., description="Token symbol")
    price_target: float = Field(..., description="Target price")
    condition: str = Field(..., description="above or below")
    wallet_address: str = Field(..., description="User's wallet address")

# Mining Data Models
class MiningRequest(BaseModel):
    coin: str = Field(..., description="Coin to mine")
    pool: str = Field(..., description="Mining pool")
    wallet_address: str = Field(..., description="Wallet address for payouts")

class GPU(BaseModel):
    id: int
    name: str
    memory: int
    power_limit: int
    temperature: float
    fan_speed: int
    core_clock_mhz: int
    memory_clock_mhz: int
    driver_version: str

class CPU(BaseModel):
    name: str
    cores: int
    threads: int
    base_clock: float
    temperature: float

class HardwareInfo(BaseModel):
    gpus: List[GPU]
    cpu: CPU
    total_memory: int
    power_supply: int

class MiningStatus(BaseModel):
    is_running: bool
    coin: str
    algorithm: str
    pool: str
    hashrate: float
    target_hashrate: float
    power_consumption: float
    efficiency: float
    temperature: float
    fan_speed: int
    accepted_shares: int
    rejected_shares: int
    uptime: str

class MiningEarnings(BaseModel):
    daily: float
    weekly: float
    monthly: float
    total: float
    daily_coin: float
    currency: str

class MiningPool(BaseModel):
    name: str
    url: str
    port: int
    fee: float
    miners: int
    hashrate: float
    luck: int
    last_block: str
    algorithm: str

class AIRecommendation(BaseModel):
    type: str
    message: str
    confidence: Optional[int]
    action: Optional[str]

class TokenBalance(BaseModel):
    token: str
    symbol: str
    balance: str
    value_usd: float
    price: float
    change_24h: float

class WalletData(BaseModel):
    address: str
    total_value_usd: float
    daily_change_percent: float
    tokens: List[TokenBalance]
    last_updated: str

class FriendWalletData(BaseModel):
    address: str
    alias: Optional[str]
    total_value_usd: float
    daily_change_percent: float
    weekly_change_percent: float
    monthly_change_percent: float
    top_tokens: List[TokenBalance]
    recent_transactions: List[Dict[str, Any]]
    ai_insights: str
    last_updated: str

class MarketData(BaseModel):
    symbol: str
    name: str
    price: float
    change_24h: float
    volume_24h: float
    market_cap: float
    trend: str

class TradeResponse(BaseModel):
    success: bool
    transaction_hash: Optional[str]
    message: str
    estimated_gas: Optional[int]
    estimated_output: Optional[float]

# In-memory storage (use Redis in production)
connected_wallets: Dict[str, WalletData] = {}
friend_wallets: Dict[str, List[str]] = {}
price_alerts: Dict[str, List[Dict]] = {}
trade_history: Dict[str, List[Dict]] = {}
mining_sessions: Dict[str, Dict] = {}  # Track active mining sessions

# Crypto Exchange Integration
class CryptoExchangeManager:
    def __init__(self):
        self.exchanges = {}
        self.init_exchanges()
    
    def init_exchanges(self):
        """Initialize crypto exchanges"""
        try:
            # Example: Binance integration (add API keys in production)
            # self.exchanges['binance'] = ccxt.binance({
            #     'apiKey': os.getenv('BINANCE_API_KEY'),
            #     'secret': os.getenv('BINANCE_SECRET'),
            #     'sandbox': True,  # Use sandbox for testing
            # })
            pass
        except Exception as e:
            logger.error(f"Failed to initialize exchanges: {e}")
    
    async def get_market_data(self) -> List[MarketData]:
        """Fetch market data from CoinGecko"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{COINGECKO_API_URL}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": 50,
                        "page": 1,
                        "sparkline": False,
                        "price_change_percentage": "24h"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [
                        MarketData(
                            symbol=coin["symbol"].upper(),
                            name=coin["name"],
                            price=coin["current_price"],
                            change_24h=coin["price_change_percentage_24h"] or 0,
                            volume_24h=coin["total_volume"] or 0,
                            market_cap=coin["market_cap"] or 0,
                            trend="bullish" if (coin["price_change_percentage_24h"] or 0) > 0 else "bearish"
                        )
                        for coin in data
                    ]
                else:
                    logger.error(f"CoinGecko API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return []

# AI Analysis Engine
class AIAnalysisEngine:
    @staticmethod
    async def analyze_wallet_behavior(address: str, transactions: List[Dict]) -> str:
        """Analyze wallet behavior patterns using AI"""
        try:
            # In production, integrate with real AI models
            patterns = [
                "This wallet demonstrates conservative DeFi strategies with consistent staking rewards",
                "High-frequency trading pattern detected with focus on momentum strategies",
                "Long-term HODLer with occasional profit-taking during market peaks",
                "Active yield farmer rotating between protocols for optimal returns",
                "Memecoin trader with quick entry/exit strategies and high risk tolerance",
                "NFT collector and trader with focus on blue-chip collections",
                "Cross-chain DeFi user maximizing opportunities across multiple networks"
            ]
            
            # Simple analysis based on transaction count and frequency
            if len(transactions) > 100:
                return "High-frequency trader with active trading patterns"
            elif len(transactions) < 10:
                return "Conservative long-term holder with minimal trading activity"
            else:
                return patterns[hash(address) % len(patterns)]
                
        except Exception as e:
            logger.error(f"Error analyzing wallet behavior: {e}")
            return "Unable to analyze wallet behavior at this time"
    
    @staticmethod
    async def generate_trading_signals() -> List[Dict[str, Any]]:
        """Generate AI-powered trading signals"""
        try:
            # Mock AI signals (integrate with real AI in production)
            signals = [
                {
                    "token": "ETH",
                    "signal": "strong_buy",
                    "confidence": 89,
                    "reasoning": "Technical indicators show bullish divergence with strong volume support",
                    "timeframe": "4h",
                    "entry_price": 2456.78,
                    "targets": [2580.00, 2720.00, 2850.00],
                    "stop_loss": 2290.00
                },
                {
                    "token": "BTC",
                    "signal": "buy",
                    "confidence": 76,
                    "reasoning": "Breaking above key resistance with institutional accumulation",
                    "timeframe": "1d",
                    "entry_price": 43250.00,
                    "targets": [45000.00, 47500.00, 50000.00],
                    "stop_loss": 41000.00
                },
                {
                    "token": "SOL",
                    "signal": "neutral",
                    "confidence": 54,
                    "reasoning": "Consolidating in range, waiting for clear direction",
                    "timeframe": "12h",
                    "entry_price": 0,
                    "targets": [],
                    "stop_loss": 0
                }
            ]
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return []

# Blockchain Data Manager
class BlockchainDataManager:
    def __init__(self):
        self.w3 = w3
    
    async def get_wallet_balance(self, address: str) -> WalletData:
        """Get wallet balance and token holdings"""
        try:
            # Validate address
            if not self.w3.is_address(address):
                raise ValueError("Invalid wallet address")
            
            # Get ETH balance
            eth_balance = self.w3.eth.get_balance(address)
            eth_balance_formatted = self.w3.from_wei(eth_balance, 'ether')
            
            # In production, integrate with APIs like Alchemy, Moralis for token balances
            # For now, return mock data
            mock_tokens = [
                TokenBalance(
                    token="ETH",
                    symbol="ETH",
                    balance=str(eth_balance_formatted),
                    value_usd=float(eth_balance_formatted) * 2456.78,
                    price=2456.78,
                    change_24h=3.45
                ),
                TokenBalance(
                    token="USDC",
                    symbol="USDC",
                    balance="5000.00",
                    value_usd=5000.00,
                    price=1.00,
                    change_24h=0.01
                )
            ]
            
            total_value = sum(token.value_usd for token in mock_tokens)
            
            return WalletData(
                address=address,
                total_value_usd=total_value,
                daily_change_percent=2.34,
                tokens=mock_tokens,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to get wallet balance: {str(e)}")
    
    async def get_transaction_history(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction history for wallet"""
        try:
            # In production, use blockchain APIs like Etherscan, Alchemy
            # Return mock transaction data
            mock_transactions = [
                {
                    "hash": "0x" + "1" * 64,
                    "from": address,
                    "to": "0x" + "a" * 40,
                    "value": "1.5",
                    "token": "ETH",
                    "type": "send",
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "gas_used": 21000,
                    "status": "success"
                },
                {
                    "hash": "0x" + "2" * 64,
                    "from": "0x" + "b" * 40,
                    "to": address,
                    "value": "100.0",
                    "token": "USDC",
                    "type": "receive",
                    "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                    "gas_used": 65000,
                    "status": "success"
                }
            ]
            
            return mock_transactions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return []

# Security Manager
class SecurityManager:
    @staticmethod
    def verify_signature(address: str, message: str, signature: str) -> bool:
        """Verify wallet signature for authentication"""
        try:
            # In production, implement proper signature verification
            # This is a simplified version
            expected_hash = hashlib.sha256(f"{address}{message}".encode()).hexdigest()
            return signature.startswith(expected_hash[:10])
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    @staticmethod
    def create_auth_token(address: str) -> str:
        """Create authentication token"""
        try:
            timestamp = str(int(time.time()))
            payload = f"{address}:{timestamp}"
            signature = hmac.new(
                SECRET_KEY.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            return f"{payload}:{signature}"
        except Exception as e:
            logger.error(f"Error creating auth token: {e}")
            return ""
    
    @staticmethod
    def verify_auth_token(token: str) -> Optional[str]:
        """Verify authentication token and return wallet address"""
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return None
            
            address, timestamp, signature = parts
            payload = f"{address}:{timestamp}"
            
            expected_signature = hmac.new(
                SECRET_KEY.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                return None
            
            # Check if token is not expired (24 hours)
            if int(time.time()) - int(timestamp) > 86400:
                return None
            
            return address
            
        except Exception as e:
            logger.error(f"Error verifying auth token: {e}")
            return None

# Initialize managers
exchange_manager = CryptoExchangeManager()
blockchain_manager = BlockchainDataManager()
ai_engine = AIAnalysisEngine()
security_manager = SecurityManager()

# Mining Management Classes
class MiningManager:
    def __init__(self):
        self.active_sessions = {}
    
    async def detect_hardware(self) -> HardwareInfo:
        """Detect available mining hardware"""
        try:
            # In production, use system APIs to detect actual hardware
            # For now, return mock hardware data
            mock_gpus = [
                GPU(
                    id=0,
                    name="NVIDIA GeForce RTX 4080",
                    memory=16,
                    power_limit=320,
                    temperature=67.5,
                    fan_speed=65,
                    core_clock_mhz=2505,
                    memory_clock_mhz=22400,
                    driver_version="531.68"
                ),
                GPU(
                    id=1,
                    name="NVIDIA GeForce RTX 4070",
                    memory=12,
                    power_limit=200,
                    temperature=62.3,
                    fan_speed=58,
                    core_clock_mhz=2475,
                    memory_clock_mhz=21000,
                    driver_version="531.68"
                )
            ]
            
            mock_cpu = CPU(
                name="AMD Ryzen 9 7950X",
                cores=16,
                threads=32,
                base_clock=4.5,
                temperature=45.2
            )
            
            return HardwareInfo(
                gpus=mock_gpus,
                cpu=mock_cpu,
                total_memory=32,
                power_supply=850
            )
            
        except Exception as e:
            logger.error(f"Error detecting hardware: {e}")
            raise HTTPException(status_code=500, detail="Failed to detect hardware")
    
    async def start_mining(self, user_address: str, coin: str, pool: str) -> Dict[str, Any]:
        """Start mining operation"""
        try:
            # In production, start actual mining process
            session_id = hashlib.md5(f"{user_address}{time.time()}".encode()).hexdigest()[:16]
            
            mining_session = {
                "session_id": session_id,
                "user_address": user_address,
                "coin": coin,
                "pool": pool,
                "algorithm": self._get_algorithm_for_coin(coin),
                "start_time": datetime.now().isoformat(),
                "status": "starting"
            }
            
            mining_sessions[user_address] = mining_session
            
            # Simulate mining startup delay
            await asyncio.sleep(1)
            
            mining_sessions[user_address]["status"] = "running"
            
            return {
                "success": True,
                "session_id": session_id,
                "message": f"Mining {coin} started successfully"
            }
            
        except Exception as e:
            logger.error(f"Error starting mining: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def stop_mining(self, user_address: str) -> Dict[str, Any]:
        """Stop mining operation"""
        try:
            if user_address in mining_sessions:
                session = mining_sessions[user_address]
                session["status"] = "stopped"
                session["end_time"] = datetime.now().isoformat()
                
                # In production, stop actual mining process
                logger.info(f"Stopping mining session {session['session_id']}")
                
                return {
                    "success": True,
                    "message": "Mining stopped successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "No active mining session found"
                }
                
        except Exception as e:
            logger.error(f"Error stopping mining: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_mining_status(self, user_address: str) -> MiningStatus:
        """Get current mining status"""
        try:
            if user_address in mining_sessions:
                session = mining_sessions[user_address]
                if session["status"] == "running":
                    # Calculate uptime
                    start_time = datetime.fromisoformat(session["start_time"])
                    uptime_seconds = (datetime.now() - start_time).total_seconds()
                    uptime_str = str(timedelta(seconds=int(uptime_seconds)))
                    
                    # Generate realistic mining metrics
                    base_hashrate = 85.6
                    hashrate = base_hashrate + (time.time() % 10) - 5  # Simulate fluctuation
                    
                    return MiningStatus(
                        is_running=True,
                        coin=session["coin"],
                        algorithm=session["algorithm"],
                        pool=session["pool"],
                        hashrate=round(hashrate, 2),
                        target_hashrate=90.0,
                        power_consumption=round(420 + (time.time() % 50), 1),
                        efficiency=round(hashrate / 420, 3),
                        temperature=round(68 + (time.time() % 8), 1),
                        fan_speed=int(65 + (time.time() % 10)),
                        accepted_shares=int(uptime_seconds / 30),
                        rejected_shares=int((time.time() % 3)),
                        uptime=uptime_str
                    )
            
            # No active mining session
            return MiningStatus(
                is_running=False,
                coin="",
                algorithm="",
                pool="",
                hashrate=0.0,
                target_hashrate=0.0,
                power_consumption=0.0,
                efficiency=0.0,
                temperature=0.0,
                fan_speed=0,
                accepted_shares=0,
                rejected_shares=0,
                uptime="00:00:00"
            )
            
        except Exception as e:
            logger.error(f"Error getting mining status: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_mining_earnings(self, user_address: str) -> MiningEarnings:
        """Calculate mining earnings"""
        try:
            # In production, calculate based on actual hashrate, pool data, and market prices
            if user_address in mining_sessions:
                session = mining_sessions[user_address]
                if session["status"] == "running":
                    # Calculate earnings based on mining time
                    start_time = datetime.fromisoformat(session["start_time"])
                    hours_mined = (datetime.now() - start_time).total_seconds() / 3600
                    
                    # Mock earning rates (USD per hour)
                    hourly_rate = 0.52
                    daily_earnings = hourly_rate * min(hours_mined, 24)
                    
                    return MiningEarnings(
                        daily=round(daily_earnings, 2),
                        weekly=round(daily_earnings * 7, 2),
                        monthly=round(daily_earnings * 30, 2),
                        total=round(daily_earnings, 2),  # Total is just current session
                        daily_coin=round(daily_earnings / 2456.78, 6),  # Mock ETH price
                        currency="USD"
                    )
            
            # No earnings if not mining
            return MiningEarnings(
                daily=0.0,
                weekly=0.0,
                monthly=0.0,
                total=0.0,
                daily_coin=0.0,
                currency="USD"
            )
            
        except Exception as e:
            logger.error(f"Error calculating earnings: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_mining_pools(self) -> List[MiningPool]:
        """Get available mining pools"""
        try:
            # In production, fetch real pool data
            pools = [
                MiningPool(
                    name="Ethermine",
                    url="eth-us-east1.nanopool.org",
                    port=9999,
                    fee=1.0,
                    miners=234567,
                    hashrate=245.7,
                    luck=103,
                    last_block="2h 34m ago",
                    algorithm="Ethash"
                ),
                MiningPool(
                    name="2Miners",
                    url="eth.2miners.com",
                    port=2020,
                    fee=1.0,
                    miners=187432,
                    hashrate=198.3,
                    luck=97,
                    last_block="1h 12m ago",
                    algorithm="Ethash"
                ),
                MiningPool(
                    name="F2Pool",
                    url="eth.f2pool.com",
                    port=6688,
                    fee=2.5,
                    miners=156789,
                    hashrate=167.9,
                    luck=108,
                    last_block="3h 45m ago",
                    algorithm="Ethash"
                ),
                MiningPool(
                    name="NiceHash",
                    url="stratum+tcp://daggerhashimoto.usa.nicehash.com",
                    port=3353,
                    fee=2.0,
                    miners=98765,
                    hashrate=123.4,
                    luck=94,
                    last_block="45m ago",
                    algorithm="DaggerHashimoto"
                )
            ]
            
            return pools
            
        except Exception as e:
            logger.error(f"Error getting mining pools: {e}")
            raise HTTPException(status_code=500, detail="Failed to get mining pools")
    
    async def benchmark_hardware(self, user_address: str) -> Dict[str, Any]:
        """Run hardware benchmark"""
        try:
            # In production, run actual benchmark tests
            logger.info(f"Starting benchmark for user {user_address}")
            
            # Simulate benchmark duration
            await asyncio.sleep(2)
            
            benchmark_results = {
                "ethash": round(85.6 + (time.time() % 10), 2),
                "kawpow": round(62.3 + (time.time() % 8), 2),
                "randomx": round(18.7 + (time.time() % 3), 2),
                "timestamp": datetime.now().isoformat(),
                "completed": True
            }
            
            return {
                "success": True,
                "results": benchmark_results,
                "message": "Benchmark completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error running benchmark: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_ai_recommendations(self, user_address: str) -> List[AIRecommendation]:
        """Get AI mining recommendations"""
        try:
            recommendations = []
            
            # Check if user is mining
            if user_address in mining_sessions:
                session = mining_sessions[user_address]
                if session["status"] == "running":
                    # Add optimization recommendations
                    recommendations.extend([
                        AIRecommendation(
                            type="optimization",
                            message="Reduce GPU core clock by 50MHz to improve efficiency by 8%",
                            confidence=87,
                            action="optimize_clocks"
                        ),
                        AIRecommendation(
                            type="warning",
                            message="GPU temperature approaching 75°C, consider increasing fan speed",
                            confidence=92,
                            action="adjust_cooling"
                        )
                    ])
            
            # Add profitability recommendations
            recommendations.append(
                AIRecommendation(
                    type="profitability",
                    message="Switch to Ravencoin mining for 15% higher profitability this week",
                    confidence=78,
                    action="switch_coin"
                )
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {e}")
            return []
    
    def _get_algorithm_for_coin(self, coin: str) -> str:
        """Get mining algorithm for coin"""
        algorithms = {
            "ETC": "Ethash",
            "RVN": "Kawpow", 
            "XMR": "RandomX",
            "BTC": "SHA-256",
            "LTC": "Scrypt"
        }
        return algorithms.get(coin, "Ethash")

# Initialize mining manager
mining_manager = MiningManager()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Get current authenticated user"""
    address = security_manager.verify_auth_token(credentials.credentials)
    if not address:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return address

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "CoresAI Crypto Trading API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "wallet_connection",
            "real_time_trading",
            "friend_tracking",
            "ai_insights",
            "price_alerts",
            "portfolio_analytics"
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "web3": w3.is_connected(),
            "exchange_api": True,  # Check actual exchange connections
            "ai_engine": True
        }
    }

@app.post("/api/v1/connect-wallet")
async def connect_wallet(request: WalletConnectionRequest):
    """Connect and verify wallet"""
    try:
        # Verify signature
        if not security_manager.verify_signature(
            request.address, request.message, request.signature
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Get wallet data
        wallet_data = await blockchain_manager.get_wallet_balance(request.address)
        connected_wallets[request.address] = wallet_data
        
        # Create auth token
        auth_token = security_manager.create_auth_token(request.address)
        
        return {
            "success": True,
            "auth_token": auth_token,
            "wallet_data": wallet_data,
            "message": "Wallet connected successfully"
        }
        
    except Exception as e:
        logger.error(f"Error connecting wallet: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/wallet/balance")
async def get_wallet_balance(current_user: str = Depends(get_current_user)):
    """Get current wallet balance and holdings"""
    try:
        wallet_data = await blockchain_manager.get_wallet_balance(current_user)
        connected_wallets[current_user] = wallet_data
        return wallet_data
        
    except Exception as e:
        logger.error(f"Error getting wallet balance: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/market-data")
async def get_market_data():
    """Get current market data"""
    try:
        market_data = await exchange_manager.get_market_data()
        return {"data": market_data, "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")

@app.post("/api/v1/trade")
async def execute_trade(
    trade_request: TradeRequest,
    current_user: str = Depends(get_current_user)
):
    """Execute a trade order"""
    try:
        if trade_request.wallet_address != current_user:
            raise HTTPException(status_code=403, detail="Unauthorized wallet address")
        
        # In production, implement actual DEX/CEX integration
        # For now, return mock response
        transaction_hash = "0x" + hashlib.sha256(
            f"{trade_request.token_in}{trade_request.token_out}{time.time()}".encode()
        ).hexdigest()
        
        # Store trade history
        if current_user not in trade_history:
            trade_history[current_user] = []
        
        trade_history[current_user].append({
            "transaction_hash": transaction_hash,
            "token_in": trade_request.token_in,
            "token_out": trade_request.token_out,
            "amount_in": trade_request.amount_in,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
        
        return TradeResponse(
            success=True,
            transaction_hash=transaction_hash,
            message="Trade executed successfully",
            estimated_gas=150000,
            estimated_output=trade_request.amount_in * 0.998  # Mock slippage
        )
        
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/friend-wallet/add")
async def add_friend_wallet(
    request: FriendWalletRequest,
    current_user: str = Depends(get_current_user)
):
    """Add friend wallet for tracking"""
    try:
        # Validate wallet address
        if not w3.is_address(request.wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address")
        
        # Add to friend list
        if current_user not in friend_wallets:
            friend_wallets[current_user] = []
        
        if request.wallet_address not in friend_wallets[current_user]:
            friend_wallets[current_user].append(request.wallet_address)
        
        # Get friend wallet data
        wallet_data = await blockchain_manager.get_wallet_balance(request.wallet_address)
        transactions = await blockchain_manager.get_transaction_history(request.wallet_address)
        ai_insights = await ai_engine.analyze_wallet_behavior(request.wallet_address, transactions)
        
        friend_data = FriendWalletData(
            address=request.wallet_address,
            alias=request.alias,
            total_value_usd=wallet_data.total_value_usd,
            daily_change_percent=wallet_data.daily_change_percent,
            weekly_change_percent=5.67,  # Mock data
            monthly_change_percent=12.34,  # Mock data
            top_tokens=wallet_data.tokens[:5],
            recent_transactions=transactions[:10],
            ai_insights=ai_insights,
            last_updated=datetime.now().isoformat()
        )
        
        return {
            "success": True,
            "friend_data": friend_data,
            "message": "Friend wallet added successfully"
        }
        
    except Exception as e:
        logger.error(f"Error adding friend wallet: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/friend-wallets")
async def get_friend_wallets(current_user: str = Depends(get_current_user)):
    """Get all tracked friend wallets"""
    try:
        if current_user not in friend_wallets:
            return {"friends": [], "count": 0}
        
        friend_data_list = []
        for address in friend_wallets[current_user]:
            wallet_data = await blockchain_manager.get_wallet_balance(address)
            transactions = await blockchain_manager.get_transaction_history(address)
            ai_insights = await ai_engine.analyze_wallet_behavior(address, transactions)
            
            friend_data = FriendWalletData(
                address=address,
                alias=None,
                total_value_usd=wallet_data.total_value_usd,
                daily_change_percent=wallet_data.daily_change_percent,
                weekly_change_percent=5.67,  # Mock data
                monthly_change_percent=12.34,  # Mock data
                top_tokens=wallet_data.tokens[:5],
                recent_transactions=transactions[:5],
                ai_insights=ai_insights,
                last_updated=datetime.now().isoformat()
            )
            
            friend_data_list.append(friend_data)
        
        return {
            "friends": friend_data_list,
            "count": len(friend_data_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting friend wallets: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/ai/trading-signals")
async def get_trading_signals():
    """Get AI-powered trading signals"""
    try:
        signals = await ai_engine.generate_trading_signals()
        return {
            "signals": signals,
            "generated_at": datetime.now().isoformat(),
            "disclaimer": "Trading signals are for informational purposes only. Always DYOR."
        }
        
    except Exception as e:
        logger.error(f"Error getting trading signals: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate trading signals")

@app.post("/api/v1/alerts/price")
async def create_price_alert(
    request: PriceAlertRequest,
    current_user: str = Depends(get_current_user)
):
    """Create price alert"""
    try:
        if current_user not in price_alerts:
            price_alerts[current_user] = []
        
        alert = {
            "id": hashlib.md5(f"{current_user}{request.token}{time.time()}".encode()).hexdigest()[:8],
            "token": request.token,
            "price_target": request.price_target,
            "condition": request.condition,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        price_alerts[current_user].append(alert)
        
        return {
            "success": True,
            "alert": alert,
            "message": "Price alert created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating price alert: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/portfolio/analytics")
async def get_portfolio_analytics(current_user: str = Depends(get_current_user)):
    """Get portfolio analytics and performance metrics"""
    try:
        # In production, calculate real metrics from transaction history
        analytics = {
            "total_return_percent": 23.45,
            "total_return_usd": 5432.10,
            "best_performing_token": {"symbol": "SOL", "return": 89.4},
            "worst_performing_token": {"symbol": "DOGE", "return": -12.3},
            "total_trades": 47,
            "win_rate": 68.1,
            "avg_hold_time_hours": 72.5,
            "sharpe_ratio": 1.23,
            "max_drawdown_percent": -15.67,
            "portfolio_diversity_score": 7.8,
            "risk_score": "Medium",
            "generated_at": datetime.now().isoformat()
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting portfolio analytics: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Mining API Endpoints
@app.get("/api/v1/mining/hardware")
async def detect_hardware():
    """Detect available mining hardware"""
    try:
        hardware_info = await mining_manager.detect_hardware()
        return {
            "success": True,
            "hardware": hardware_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error detecting hardware: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect hardware")

@app.post("/api/v1/mining/start")
async def start_mining(
    request: MiningRequest,
    current_user: str = Depends(get_current_user)
):
    """Start mining operation"""
    try:
        if request.wallet_address != current_user:
            raise HTTPException(status_code=403, detail="Unauthorized wallet address")
        
        result = await mining_manager.start_mining(current_user, request.coin, request.pool)
        return result
        
    except Exception as e:
        logger.error(f"Error starting mining: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/mining/stop")
async def stop_mining(current_user: str = Depends(get_current_user)):
    """Stop mining operation"""
    try:
        result = await mining_manager.stop_mining(current_user)
        return result
        
    except Exception as e:
        logger.error(f"Error stopping mining: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/mining/status")
async def get_mining_status(current_user: str = Depends(get_current_user)):
    """Get current mining status"""
    try:
        status = await mining_manager.get_mining_status(current_user)
        return status
        
    except Exception as e:
        logger.error(f"Error getting mining status: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/mining/earnings")
async def get_mining_earnings(current_user: str = Depends(get_current_user)):
    """Get mining earnings"""
    try:
        earnings = await mining_manager.get_mining_earnings(current_user)
        return earnings
        
    except Exception as e:
        logger.error(f"Error getting mining earnings: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/mining/pools")
async def get_mining_pools():
    """Get available mining pools"""
    try:
        pools = await mining_manager.get_mining_pools()
        return {
            "pools": pools,
            "count": len(pools),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting mining pools: {e}")
        raise HTTPException(status_code=500, detail="Failed to get mining pools")

@app.post("/api/v1/mining/benchmark")
async def benchmark_hardware(current_user: str = Depends(get_current_user)):
    """Run hardware benchmark"""
    try:
        result = await mining_manager.benchmark_hardware(current_user)
        return result
        
    except Exception as e:
        logger.error(f"Error running benchmark: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/mining/ai-recommendations")
async def get_ai_mining_recommendations(current_user: str = Depends(get_current_user)):
    """Get AI mining recommendations"""
    try:
        recommendations = await mining_manager.get_ai_recommendations(current_user)
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting AI recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI recommendations")

@app.get("/api/v1/mining/algorithms")
async def get_supported_algorithms():
    """Get supported mining algorithms"""
    try:
        algorithms = {
            "Ethash": {
                "coins": ["ETC", "ETH"],
                "description": "Memory-hard algorithm used by Ethereum Classic",
                "hardware": ["GPU"]
            },
            "Kawpow": {
                "coins": ["RVN"],
                "description": "Modified version of ProgPow used by Ravencoin",
                "hardware": ["GPU"]
            },
            "RandomX": {
                "coins": ["XMR"],
                "description": "CPU-optimized algorithm used by Monero",
                "hardware": ["CPU"]
            },
            "SHA-256": {
                "coins": ["BTC"],
                "description": "Hash function used by Bitcoin",
                "hardware": ["ASIC"]
            },
            "Scrypt": {
                "coins": ["LTC"],
                "description": "Memory-hard algorithm used by Litecoin",
                "hardware": ["ASIC", "GPU"]
            }
        }
        
        return {
            "algorithms": algorithms,
            "count": len(algorithms)
        }
        
    except Exception as e:
        logger.error(f"Error getting algorithms: {e}")
        raise HTTPException(status_code=500, detail="Failed to get algorithms")

# --- Crypto Pool System ---
pools = {}
pool_boosts = {}

@app.post("/api/v1/pools/create")
async def create_pool(data: dict = Body(...)):
    """Create a new crypto pool"""
    pool_id = str(len(pools) + 1)
    pools[pool_id] = {
        "id": pool_id,
        "name": data.get("name", f"Pool {pool_id}"),
        "privacy": data.get("privacy", "private"),
        "split_mode": data.get("split_mode", "equal"),
        "members": [data.get("creator")],
        "size": 0,
        "return_pct": 0,
        "trades": [],
        "logs": [],
    }
    return {"success": True, "pool_id": pool_id, "pool": pools[pool_id]}

@app.post("/api/v1/pools/invite")
async def invite_to_pool(data: dict = Body(...)):
    """Invite a user to a pool"""
    pool_id = data["pool_id"]
    address = data["address"]
    pools[pool_id]["members"].append(address)
    pools[pool_id]["logs"].append({"action": "invite", "address": address})
    return {"success": True}

@app.post("/api/v1/pools/join")
async def join_pool(data: dict = Body(...)):
    """Join a pool (public or with invite)"""
    pool_id = data["pool_id"]
    address = data["address"]
    pools[pool_id]["members"].append(address)
    pools[pool_id]["logs"].append({"action": "join", "address": address})
    return {"success": True}

@app.get("/api/v1/pools/status/{pool_id}")
async def get_pool_status(pool_id: str):
    """Get pool status (size, members, trades, P/L, payouts)"""
    return pools.get(pool_id, {})

@app.post("/api/v1/pools/trade")
async def execute_pool_trade(data: dict = Body(...)):
    """Execute a trade for the pool"""
    pool_id = data["pool_id"]
    trade = data["trade"]
    pools[pool_id]["trades"].append(trade)
    pools[pool_id]["logs"].append({"action": "trade", "trade": trade})
    return {"success": True}

@app.post("/api/v1/pools/deposit")
async def deposit_to_pool(data: dict = Body(...)):
    """Deposit funds to the pool"""
    pool_id = data["pool_id"]
    amount = data["amount"]
    pools[pool_id]["size"] += amount
    pools[pool_id]["logs"].append({"action": "deposit", "amount": amount})
    return {"success": True}

@app.post("/api/v1/pools/withdraw")
async def withdraw_from_pool(data: dict = Body(...)):
    """Withdraw funds from the pool"""
    pool_id = data["pool_id"]
    amount = data["amount"]
    pools[pool_id]["size"] -= amount
    pools[pool_id]["logs"].append({"action": "withdraw", "amount": amount})
    return {"success": True}

@app.get("/api/v1/pools/logs/{pool_id}")
async def get_pool_logs(pool_id: str):
    """Get full action log for the pool"""
    return {"logs": pools.get(pool_id, {}).get("logs", [])}

# --- Boost Spinner Logic ---
import random, time

@app.post("/api/v1/pools/boost/spin")
async def spin_boost(data: dict = Body(...)):
    """Spin the boost wheel (host only, once per 14 days)"""
    pool_id = data["pool_id"]
    now = int(time.time())
    last_spin = pool_boosts.get(pool_id, {}).get("last_spin", 0)
    if now - last_spin < 14 * 24 * 3600:
        return {"success": False, "error": "Spin not available yet"}
    boost_values = [250, 300, 450, 500]
    boost = random.choice(boost_values)
    pool_boosts[pool_id] = {
        "boost": boost,
        "last_spin": now,
        "boost_ends": now + 7 * 24 * 3600
    }
    pools[pool_id]["logs"].append({"action": "boost_spin", "boost": boost})
    return {"success": True, "boost": boost}

@app.get("/api/v1/pools/boost/status/{pool_id}")
async def get_boost_status(pool_id: str):
    """Get current boost, countdown, and bonus generated"""
    boost_info = pool_boosts.get(pool_id, {})
    now = int(time.time())
    countdown = max(0, (boost_info.get("last_spin", 0) + 14 * 24 * 3600) - now)
    boost_active = now < boost_info.get("boost_ends", 0)
    boost_ends_in = max(0, boost_info.get("boost_ends", 0) - now)
    return {
        "boost": boost_info.get("boost"),
        "boost_active": boost_active,
        "boost_ends_in": boost_ends_in,
        "countdown": countdown
    }

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "crypto_trading_backend:app",
        host="0.0.0.0",
        port=8082,
        reload=True,
        log_level="info"
    ) 