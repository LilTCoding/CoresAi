# CoresAi: Advanced AI Crypto Trading Assistant

CoresAi is an advanced AI-driven crypto trading assistant that offers a comprehensive suite of features for live trading, portfolio management, AI signals, and more. The latest addition is the Crypto Pool system, which allows users to create and manage crypto trading pools with innovative features like the Boost Spinner widget.

## Features

- **Live Trading**: Execute trades in real-time with AI-driven insights.
- **Portfolio Dashboards**: Visualize and manage your crypto assets.
- **AI Signals**: Receive AI-generated trading signals to optimize your strategy.
- **Friend Earnings Tracker**: Monitor and compare earnings with friends.
- **Crypto Pool System**: Create and manage trading pools, invite members, and utilize the Boost Spinner for earnings boosts.

## Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. **Create a `.env` file with your API keys**:
   ```
   OPENAI_API_KEY=your_api_key_here
   INFURA_PROJECT_ID=your_infura_project_id
   ```

## Project Structure

```
├── frontend/          # React frontend components
├── backend/           # FastAPI backend services
├── contracts/         # Solidity smart contracts
├── tests/             # Test files
├── data/              # Data storage
└── notebooks/         # Jupyter notebooks for experiments
```

## Usage

1. **Start the API server**:
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Start the React frontend**:
   ```bash
   npm start
   ```

3. **Access the API documentation** at `http://localhost:8000/docs`

## Contributing

We welcome contributions! Feel free to submit issues and enhancement requests. 