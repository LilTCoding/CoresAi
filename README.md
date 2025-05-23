# CoresAI - Advanced AI Trading System

![CoresAI Logo](dragon_logo.png)

## Overview

CoresAI is a comprehensive AI-powered trading system that combines advanced algorithmic trading, social features, and Discord integration. The system includes multiple specialized backends, a React frontend, and a Discord bot for community interaction.

## Features

### Core Components
- 🤖 **AI Trading Engine**: Advanced algorithmic trading with real-time market analysis
- 💹 **Crypto Pool System**: Social trading pools with shared strategies and earnings
- 🎲 **Boost Spinner**: Unique reward system for pool participants
- 🤝 **Friend Earnings Tracker**: Monitor and compare trading performance
- 🔔 **Alert System**: Customizable price and trend alerts
- 📊 **Portfolio Analytics**: Detailed performance metrics and insights

### Discord Integration
- 📊 **Market Analysis Channel**: Technical analysis and market data
- 💹 **Trading Room**: Execute trades and manage positions
- 🔔 **Price Alerts**: Real-time price monitoring
- 🧪 **Strategy Lab**: Create and test trading strategies
- 🤖 **AI Chat**: AI-powered trading assistant
- 📰 **News Feed**: Market news and updates
- 📚 **Learning Center**: Trading education resources

## System Architecture

### Backend Services
- Production Backend (Port 8082): Main AI and trading functionality
- Streaming Backend (Port 8081): Real-time data streaming
- Crypto Backend (Port 8083): Cryptocurrency trading operations
- Discord Bot: Community interaction and trading commands

### Frontend
- React-based dashboard
- Real-time market data visualization
- Portfolio management interface
- Social trading features

## Installation

### Prerequisites
- Python 3.13
- Node.js (Latest LTS)
- Redis Server
- Discord Bot Token (for Discord integration)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CoresAi.git
cd CoresAi
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
pip install -r crypto_requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

5. Configure environment variables:
- Copy `.env.example` to `.env`
- Fill in required API keys and tokens

6. Configure Discord bot:
- Update `config.py` with your Discord bot token and channel IDs

## Running the System

### Option 1: Using the Safe Start Script (Recommended)
```bash
start_coresai_safe.bat  # Windows
./start_coresai_safe.sh # Linux/Mac
```

### Option 2: Manual Startup
1. Start the backends:
```bash
uvicorn production_ai_backend:app --host 0.0.0.0 --port 8082
uvicorn streaming_ai_backend:app --host 0.0.0.0 --port 8081
uvicorn crypto_trading_backend:app --host 0.0.0.0 --port 8083
```

2. Start the frontend:
```bash
cd frontend
npm start
```

3. Start the Discord bot:
```bash
python run_bot.py
```

## API Documentation

### Production Backend (8082)
- `/api/v1/chat`: AI chat endpoint
- `/api/v1/trade`: Execute trades
- `/api/v1/portfolio`: Portfolio management
- `/api/v1/market-data`: Market analysis

### Streaming Backend (8081)
- `/api/v1/stream-object`: Real-time data streaming
- `/api/v1/price-feed`: Live price updates
- `/api/v1/alerts`: Price alerts

### Crypto Backend (8083)
- `/api/v1/pools`: Crypto pool management
- `/api/v1/mining`: Mining operations
- `/api/v1/boost`: Boost spinner system

## Development

### Directory Structure
```
CoresAi/
├── src/                 # Backend source code
├── frontend/           # React frontend
├── data/              # Data storage
├── models/            # AI models
├── scripts/           # Utility scripts
├── servers/           # Game server integrations
└── tests/             # Test suites
```

### Testing
```bash
python -m pytest tests/
```

### Deployment
1. Build frontend:
```bash
cd frontend
npm run build
```

2. Deploy to Vercel:
```bash
vercel deploy
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For support and updates:
- Discord: [Join our server](https://discord.gg/coresai)
- Documentation: [docs.coresai.com](https://docs.coresai.com)
- Issues: [GitHub Issues](https://github.com/yourusername/CoresAi/issues)

## Acknowledgments

- Thanks to all contributors
- Special thanks to the trading community
- Built with ❤️ by the CoresAI team 