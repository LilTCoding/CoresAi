#!/bin/bash

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Start backend server
echo "Starting backend server..."
python -m uvicorn src.app:app --host 0.0.0.0 --port 8082 --reload &

# Start frontend development server
echo "Starting frontend server..."
npm start 