# CoresAI Crypto Trading Assistant

An advanced AI-powered crypto trading assistant with live wallet integration, social earnings analytics, and intelligent mining optimization, designed with the futuristic CoresAi aesthetic.

## 🚀 Features

### 🔁 Live Trading Module
- **Secure Wallet Integration**: MetaMask, WalletConnect, Ledger support
- **Multi-Blockchain Support**: Ethereum, Bitcoin, BNB Chain, Solana, Polygon
- **Real-time Portfolio Dashboard**: Live balances, P&L tracking, gas fees
- **AI Trading Signals**: Machine learning-powered buy/sell recommendations
- **Advanced Order Types**: Limit orders, stop-loss, take-profit strategies
- **DEX/CEX Integration**: Uniswap, PancakeSwap, Binance, Coinbase support
- **Transaction Tracking**: Real-time hash tracking and confirmation

### 🧑‍🤝‍🧑 Friend Earnings Tracker
- **Social Analytics**: Track friends' and influencers' wallet performance
- **Portfolio Insights**: Real-time wallet values, holdings, and trends
- **AI Behavior Analysis**: Advanced pattern recognition and insights
- **Performance Metrics**: 24h/7d/30d profit/loss tracking
- **Watchlist Management**: Organize wallets into custom groups
- **Live Updates**: Real-time data synchronization

### ⛏️ AI-Powered Crypto Miner (NEW!)
- **Hardware Detection**: Automatic GPU and CPU detection with specs
- **Multi-Algorithm Support**: Ethash, Kawpow, RandomX, SHA-256, Scrypt, Octa
- **Supported Coins**: Ethereum Classic (ETC), Ravencoin (RVN), Monero (XMR), Bitcoin (BTC), Litecoin (LTC)
- **AI Optimization**: Real-time undervolting, overclocking, and algorithm switching
- **Live Performance Monitoring**: Hashrate, power consumption, temperature, fan speed, efficiency
- **Earnings Tracking**: Projected and actual earnings per hour/day/week/month
- **Pool Management**: Ethermine, 2Miners, F2Pool, NiceHash integration
- **Hardware Benchmarking**: Performance testing across different algorithms
- **Smart Recommendations**: AI-powered profitability and optimization suggestions
- **Security First**: Transparent resource usage, no hidden processes
- **Schedule Mining**: Auto-start, overnight mining, low-power modes

### ⚡ AI-Powered Features
- **Smart Trading Signals**: 89% confidence algorithmic recommendations
- **Risk Assessment**: Real-time volatility and market risk analysis
- **Behavioral Analysis**: Pattern recognition for trading strategies
- **Market Insights**: Volume analysis, trend detection, sentiment tracking
- **Mining Intelligence**: Hardware optimization and profitability analysis

### 🔒 Security & Compliance
- **No Private Key Storage**: Secure signature-based authentication
- **2FA Integration**: Biometric and multi-factor authentication
- **Encrypted Connections**: End-to-end encryption for all wallet interactions
- **Audit Logging**: Complete transaction and recommendation history
- **KYC/AML Compliance**: Regulatory compliance for exchange integration
- **Transparent Mining**: Full visibility into mining processes and resource usage

## 🛠 Setup Instructions

### Prerequisites
- Node.js 16+ (for frontend)
- Python 3.8+ (for backend)
- MetaMask or compatible Web3 wallet
- Infura/Alchemy API key (for blockchain data)
- Mining Hardware (GPU/CPU for mining module)
- Optional: Redis (for production caching)

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**
   Create a `.env` file in the frontend directory:
   ```env
   REACT_APP_CRYPTO_API_URL=http://localhost:8082
   REACT_APP_ENVIRONMENT=development
   ```

3. **Start Frontend**
   ```bash
   npm start
   ```

### Backend Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r crypto_requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
   SECRET_KEY=your-secret-key-here-change-in-production
   REDIS_URL=redis://localhost:6379
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_SECRET=your_binance_secret
   COINGECKO_API_KEY=your_coingecko_api_key
   ```

3. **Start Backend (Windows)**
   ```bash
   start_crypto_backend.bat
   ```

4. **Start Backend (Linux/Mac)**
   ```bash
   python crypto_trading_backend.py
   ```

### Quick Start Script

For Windows users, simply run:
```bash
start_crypto_backend.bat
```

This will automatically:
- Create a virtual environment
- Install all dependencies
- Set up environment variables
- Start the crypto trading backend

## 📡 API Endpoints

### Authentication
- `POST /api/v1/connect-wallet` - Connect and verify wallet
- `GET /api/v1/wallet/balance` - Get wallet balance and holdings

### Trading
- `POST /api/v1/trade` - Execute trade orders
- `GET /api/v1/market-data` - Get real-time market data
- `GET /api/v1/ai/trading-signals` - Get AI trading recommendations

### Friend Tracking
- `POST /api/v1/friend-wallet/add` - Add friend wallet to tracking
- `GET /api/v1/friend-wallets` - Get all tracked friend wallets

### Mining (NEW!)
- `GET /api/v1/mining/hardware` - Detect available mining hardware
- `POST /api/v1/mining/start` - Start mining operation
- `POST /api/v1/mining/stop` - Stop mining operation
- `GET /api/v1/mining/status` - Get current mining status
- `GET /api/v1/mining/earnings` - Get mining earnings data
- `GET /api/v1/mining/pools` - Get available mining pools
- `POST /api/v1/mining/benchmark` - Run hardware benchmark
- `GET /api/v1/mining/ai-recommendations` - Get AI mining recommendations
- `GET /api/v1/mining/algorithms` - Get supported mining algorithms

### Analytics
- `GET /api/v1/portfolio/analytics` - Get portfolio performance metrics
- `POST /api/v1/alerts/price` - Create price alerts

### Documentation
Visit `http://localhost:8082/docs` for interactive API documentation.

## 🎨 User Interface

### Design Theme
- **Color Scheme**: Dark UI with chrome-blue and midnight accents
- **Typography**: Bold, clear fonts with 15px button text
- **Layout**: 1920x1080 optimized, responsive design
- **Animations**: Smooth framer-motion transitions
- **Icons**: Heroicons with gradient effects

### Navigation
Access the crypto trading assistant through the main navigation:
1. Click "Crypto Trading" in the navbar
2. Choose between "Live Trading", "Friend Tracker", and "AI Miner" tabs
3. Connect your wallet to begin trading or start mining

### Mining Interface Layout
- **Left Panel**: Mining control with hardware info, coin/pool selection, start/stop buttons
- **Center Panel**: Live performance stats (hashrate, power, temperature, shares)
- **Right Panel**: Earnings tracking and AI recommendations
- **Bottom Panels**: Pool statistics and performance history charts

## 🔧 Configuration Options

### Wallet Providers
```javascript
// Supported wallet providers
const WALLET_PROVIDERS = {
  METAMASK: 'MetaMask',
  WALLETCONNECT: 'WalletConnect',
  LEDGER: 'Ledger',
  COINBASE: 'Coinbase Wallet'
};
```

### Supported Networks
```javascript
const SUPPORTED_NETWORKS = {
  ETHEREUM: { chainId: 1, name: 'Ethereum' },
  POLYGON: { chainId: 137, name: 'Polygon' },
  BSC: { chainId: 56, name: 'BNB Chain' },
  ARBITRUM: { chainId: 42161, name: 'Arbitrum' }
};
```

### Mining Algorithms
```javascript
const MINING_ALGORITHMS = {
  ETHASH: { coins: ['ETC'], hardware: ['GPU'] },
  KAWPOW: { coins: ['RVN'], hardware: ['GPU'] },
  RANDOMX: { coins: ['XMR'], hardware: ['CPU'] },
  SHA256: { coins: ['BTC'], hardware: ['ASIC'] },
  SCRYPT: { coins: ['LTC'], hardware: ['ASIC', 'GPU'] }
};
```

### Trading Pairs
```javascript
const TRADING_PAIRS = [
  'ETH/USDC', 'BTC/USDT', 'SOL/USDC',
  'MATIC/ETH', 'BNB/BUSD', 'AVAX/USDC'
];
```

## 🧠 AI Features

### Trading Signal Confidence Levels
- **90-100%**: Strong Buy/Sell - High confidence signals
- **70-89%**: Buy/Sell - Medium confidence signals
- **50-69%**: Neutral - Hold or wait for better entry
- **Below 50%**: No Signal - Insufficient data

### Mining AI Recommendations
- **Optimization**: Hardware settings for maximum efficiency
- **Profitability**: Coin switching recommendations based on market conditions
- **Warning**: Temperature, power, or performance alerts

### Risk Assessment
- **Low Risk**: Blue-chip tokens, established DeFi protocols
- **Medium Risk**: Mid-cap tokens, newer protocols
- **High Risk**: Meme coins, experimental tokens

### Behavioral Analysis Patterns
- **HODLer**: Long-term holding with minimal trading
- **Day Trader**: High-frequency trading with quick entries/exits
- **DeFi Farmer**: Yield farming and liquidity provision
- **NFT Trader**: Focus on NFT collections and trading
- **Arbitrageur**: Cross-chain and cross-exchange arbitrage
- **Miner**: Focus on mining operations and hardware optimization

## 🔐 Security Best Practices

### For Users
1. **Never share private keys** - Use signature-based authentication only
2. **Verify transaction details** - Always confirm trade parameters
3. **Use hardware wallets** - Ledger/Trezor for enhanced security
4. **Enable 2FA** - Additional authentication layer
5. **Regular security audits** - Monitor wallet activity
6. **Mining safety** - Monitor temperatures and power consumption

### For Developers
1. **Secure API keys** - Use environment variables, never commit to code
2. **Rate limiting** - Implement API rate limits to prevent abuse
3. **Input validation** - Sanitize all user inputs
4. **Encrypted storage** - Encrypt sensitive data at rest
5. **Regular updates** - Keep dependencies updated
6. **Hardware monitoring** - Safe mining operation limits

## 📊 Performance Metrics

### Portfolio Analytics
- **Total Return**: Overall portfolio performance percentage
- **Sharpe Ratio**: Risk-adjusted return measurement
- **Max Drawdown**: Largest portfolio decline from peak
- **Win Rate**: Percentage of profitable trades
- **Average Hold Time**: Mean duration of positions

### Mining Performance
- **Hashrate**: Mining power in MH/s or TH/s
- **Power Efficiency**: MH/W ratio for cost analysis
- **Temperature Management**: GPU/CPU temperature monitoring
- **Uptime**: Mining session duration and stability
- **Share Acceptance**: Pool submission success rate

### Friend Tracker Metrics
- **Portfolio Value**: Real-time USD value of holdings
- **Daily/Weekly/Monthly Changes**: Performance over time periods
- **Top Holdings**: Largest positions by value and percentage
- **Trading Activity**: Recent transaction volume and frequency

## 🚨 Risk Disclaimer

**IMPORTANT**: This crypto trading and mining assistant is for educational and informational purposes only. Cryptocurrency trading and mining involve substantial risk of loss and are not suitable for all investors.

- **Not Financial Advice**: All AI signals and recommendations are not financial advice
- **DYOR**: Always Do Your Own Research before making trading decisions
- **Risk Management**: Never invest more than you can afford to lose
- **Hardware Safety**: Monitor mining equipment to prevent damage or fire hazards
- **Regulatory Compliance**: Ensure compliance with local laws and regulations
- **Power Costs**: Consider electricity costs in mining profitability calculations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, questions, or feature requests:
- Create an issue on GitHub
- Join our Discord community
- Email: support@coresai.dev

## 🔮 Roadmap

### Phase 1 (Current)
- ✅ Basic wallet connection
- ✅ Portfolio tracking
- ✅ Friend wallet monitoring
- ✅ AI trading signals
- ✅ Hardware detection and mining
- ✅ AI mining optimization

### Phase 2 (Next)
- 🔄 Advanced order types
- 🔄 Multi-chain support
- 🔄 DeFi protocol integration
- 🔄 Mobile app
- 🔄 Real-time mining pools integration
- 🔄 Advanced mining scheduling

### Phase 3 (Future)
- 📋 Copy trading features
- 📋 Social trading platform
- 📋 Advanced AI models
- 📋 Institutional features
- 📋 Mining farm management
- 📋 Cross-platform mining software

---

**Built with ❤️ by the CoresAI Team**

*Empowering traders and miners with AI-powered insights and optimization* 