"""
CoresAI Configuration
Contains all configuration settings and environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_CLIENT_ID = "1375549395508133959"
DISCORD_CLIENT_SECRET = "9501s8CKS4BrRj81rmCO-z5aZS9_8CSa"
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_REDIRECT_URI = "http://localhost:3000/auth/discord/callback"

# Discord Channel IDs
GUILD_ID = os.getenv('GUILD_ID')
CATEGORY_ID = os.getenv('CATEGORY_ID')
UPDATES_CHANNEL_ID = os.getenv('UPDATES_CHANNEL_ID')
LOGS_CHANNEL_ID = os.getenv('LOGS_CHANNEL_ID')
OWNER_ID = os.getenv('OWNER_ID')

# JWT Configuration
JWT_SECRET = "coresai-jwt-secret-key"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 24

# Frontend Configuration
FRONTEND_URL = "http://localhost:3000"
API_URL = os.getenv('API_URL', 'http://localhost:8000')
API_KEY = os.getenv('API_KEY')

# Trading Configuration
TRADING_ENABLED = os.getenv('TRADING_ENABLED', 'false').lower() == 'true'
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '10000'))
RISK_PERCENTAGE = float(os.getenv('RISK_PERCENTAGE', '2'))

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'coresai.log')

# Market Data Configuration
MARKET_DATA_PROVIDER = os.getenv('MARKET_DATA_PROVIDER', 'yahoo')
MARKET_DATA_API_KEY = os.getenv('MARKET_DATA_API_KEY')

# Alert System Configuration
MAX_ALERTS_PER_USER = int(os.getenv('MAX_ALERTS_PER_USER', '10'))
ALERT_CHECK_INTERVAL = int(os.getenv('ALERT_CHECK_INTERVAL', '60'))  # seconds

# Strategy Configuration
MAX_STRATEGIES_PER_USER = int(os.getenv('MAX_STRATEGIES_PER_USER', '5'))
BACKTEST_MAX_PERIOD = os.getenv('BACKTEST_MAX_PERIOD', '5y') 