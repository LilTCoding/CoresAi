# CoresAI: Advanced Multi-Backend AI System

CoresAI is a sophisticated AI-powered system that combines crypto trading, game server management, and advanced AI capabilities in a modern PyQt5-based interface. The system features multiple specialized backends and real-time processing capabilities.

## Core Features

### Crypto Trading & Mining
- **Wallet Management**: Connect and manage multiple cryptocurrency wallets
- **Mining Controls**: Advanced mining interface with real-time hardware monitoring
- **Multi-Coin Support**: Support for ETC, RVN, XMR, BTC, LTC
- **Mining Pool Integration**: Compatible with Ethermine, 2Miners, F2Pool, NiceHash
- **Hardware Monitoring**: Real-time tracking of CPU, GPU, memory usage
- **Mining Analytics**: Hashrate, power consumption, temperature monitoring
- **Boost Spinner**: Visual performance optimization widget

### Game Server Management
- **Multi-Game Support**:
  - FiveM QB Core
  - Minecraft
  - Arma Reforger
  - Rust
- **File Management**: Built-in file editor with AI assistance
- **Server Monitoring**: Real-time status and performance tracking
- **AI-Powered Assistance**: Get game-specific configuration help

### AI Capabilities
- **Natural Language Processing**: Advanced context-aware conversations
- **Web Search Integration**: Real-time information gathering
- **Structured Streaming**: Multiple response modes for different use cases
- **Creative Software Knowledge**: Expert guidance for:
  - Adobe Photoshop
  - Blender
  - VEGAS Pro

## Technical Architecture

### Backend Services
1. **Production Backend (Port 8082)**
   - Web search capabilities
   - Enhanced reasoning
   - Real-time data processing
   - Advanced AI features

2. **Streaming Backend (Port 8081)**
   - Structured streaming
   - Object mode processing
   - Array mode handling
   - Schema-free responses

3. **Simple Backend (Port 8080)**
   - Basic chat functionality
   - Lightweight processing
   - Quick responses

### Frontend Components
- **Modern PyQt5 GUI**
  - Dark theme interface
  - Responsive layouts
  - Real-time updates
  - Hardware monitoring widgets
  - Boost Spinner visualization

### Security Features
- CORS protection
- Input validation
- Rate limiting (optional)
- SSL support (configurable)

## System Requirements

### Software Dependencies
```bash
Python >= 3.8
Node.js (for frontend development)
```

### Key Python Packages
- FastAPI
- PyQt5
- Pydantic
- Uvicorn
- Requests
- NumPy
- Psutil
- WMI
- Cryptography
- WebSockets
- aiohttp

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/CoresAi.git
   cd CoresAi
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   Create a `.env` file with necessary API keys:
   ```env
   OPENAI_API_KEY=your_api_key
   INFURA_PROJECT_ID=your_infura_id
   ```

## Usage

1. **Start the Backend Services**:
   ```bash
   python production_ai_backend.py
   ```

2. **Launch the GUI**:
   ```bash
   python gui_app.py
   ```

3. **Access API Documentation**:
   - Production API: http://localhost:8082/docs
   - Streaming API: http://localhost:8081/docs

## Development Features

- Hot reloading support
- Debug mode (configurable)
- Test endpoints
- Performance monitoring
- Structured logging

## Project Structure
```
├── backend/           # Backend service modules
├── frontend/         # Frontend React components
├── gui/              # PyQt5 GUI components
├── models/           # AI model configurations
├── utils/            # Utility functions
├── config/           # Configuration files
└── docs/             # Documentation
```

## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details

## Version

Current Version: 4.1.0

## Support

For issues and feature requests, please use the GitHub issue tracker. 