#!/bin/bash

echo "🚀 Starting Cross-Chain Gas Fee Tracker Bot..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your API keys."
    echo "   Copy .env.example to .env and fill in your credentials."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
if ! /usr/bin/python3 -c "import telegram" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Start the bot
echo "🤖 Starting bot..."
/usr/bin/python3 main.py
