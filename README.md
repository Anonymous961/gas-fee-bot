# ⛽ Cross-Chain Gas Fee Tracker Bot

A Telegram bot that monitors real-time gas fees across multiple blockchains (Ethereum, BSC, Polygon) and sends alerts when fees drop below user-defined thresholds.

![alt text](image.png)

## ✨ Features

- **Multi-Chain Support**: Track gas fees on Ethereum, BSC, Polygon, and more
- **Smart Alerts**: Get notified when fees drop below your custom threshold
- **Real-Time Data**: Fetches live gas prices from blockchain explorers
- **User-Friendly**: Simple commands with intuitive responses
- **Scheduled Checks**: Automatic background monitoring every 10 seconds

## 🛠️ Tech Stack

- **Core**: Python 3.10+
- **Telegram Bot**: `python-telegram-bot` library
- **APIs**: Etherscan, BscScan, PolygonScan
- **Scheduler**: APScheduler
- **Database**: SQLite
- **Deployment**: Docker + AWS EC2/VPS

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Telegram Bot Token ([Get from @BotFather](https://t.me/BotFather))
- Free API keys from:
  - [Etherscan](https://etherscan.io/apis)
  - [BscScan](https://bscscan.com/apis)
  - [PolygonScan](https://polygonscan.com/apis)

### Installation & Setup

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd cross-chain-gasfee-tracker
   ```

2. **Create virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and bot token
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## 🤖 Bot Commands

| Command                    | Description             | Example               |
| -------------------------- | ----------------------- | --------------------- |
| `/start`                   | Show welcome message    | `/start`              |
| `/setalert <chain> <gwei>` | Set price alert         | `/setalert polygon 5` |
| `/myalerts`                | View your active alerts | `/myalerts`           |

## 🏗️ Project Structure

```
cross-chain-gasfee-tracker/
├── core/               # Main logic
│   ├── gas_tracker.py  # API interactions
│   ├── alert_manager.py # Alert processing
│   └── scheduler.py    # Background checks
├── bot/                # Telegram handlers
│   ├── command.py      # Command logic
│   └── bot_init.py     # Bot setup
├── data/               # Database files
├── config/             # API keys and constants
├── .env                # Environment variables
└── main.py             # Entry point
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
ETHERSCAN_API_KEY=your_etherscan_api_key
BSCSCAN_API_KEY=your_bscscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key
```

### Supported Chains

- **Ethereum (ETH)**: Chain ID 1
- **BSC**: Chain ID 56
- **Polygon**: Chain ID 137

## 🚀 Deployment

### Option 1: Local Development

```bash
# Run in terminal
source .venv/bin/activate
python main.py
```

### Option 2: Background Process

```bash
# Run persistently using tmux
tmux new -s gasbot
source .venv/bin/activate
python main.py
# Ctrl+B then D to detach
```

### Option 3: Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Error: No module named 'telegram'**

   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Event Loop Error**

   - The bot automatically handles this - no action needed

3. **API Timeout Errors**

   - Normal for free API tiers - bot will retry automatically

4. **Bot Not Responding**
   - Check if bot token is correct in .env
   - Verify bot is running: `ps aux | grep python`

### Logs

The bot provides real-time feedback:

- ✅ Database initialized
- ✅ Scheduler started
- ✅ Bot is running
- 🚨 Gas alerts sent
- ⚠️ API errors (handled automatically)

## 📈 Roadmap

- [ ] Add Solana and Avalanche support
- [ ] Implement gas fee predictions (AI)
- [ ] Create web dashboard for analytics
- [ ] Multi-language support
- [ ] Advanced alert types (time-based, trend-based)

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all dependencies are installed correctly
4. Verify your API keys are valid and have sufficient quota
