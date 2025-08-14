# ⛽ Cross-Chain Gas Fee Tracker Bot

A feature-rich Telegram bot that monitors real-time gas fees across multiple blockchains (Ethereum, BSC, Polygon) and sends smart alerts when fees drop below user-defined thresholds. Now with enhanced UI, decimal support, and comprehensive alert management!

![alt text](image.png)

## ✨ Features

- **Multi-Chain Support**: Track gas fees on Ethereum, BSC, Polygon, and more
- **Smart Alerts**: Get notified when fees drop below your custom threshold (supports decimals like 0.8 Gwei!)
- **Real-Time Data**: Fetches live gas prices from blockchain explorers every 2 minutes
- **User-Friendly**: Rich interface with emojis, inline keyboards, and intuitive commands
- **Alert Management**: View, set, and delete your gas price alerts
- **Visual Indicators**: Color-coded gas prices (🟢 Low, 🟡 Medium, 🔴 High)
- **Decimal Support**: Set precise thresholds like 0.8, 1.5, or 2.3 Gwei

## 🛠️ Tech Stack

- **Core**: Python 3.10+
- **Telegram Bot**: `python-telegram-bot` library
- **APIs**: Etherscan, BscScan, PolygonScan
- **Scheduler**: APScheduler with background monitoring
- **Database**: SQLite with decimal support
- **Deployment**: Docker + AWS EC2/VPS ready

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
   ./start.sh
   # Or manually: python main.py
   ```

## 🤖 Bot Commands

| Command     | Description             | Example     |
| ----------- | ----------------------- | ----------- |
| `/start`    | Show main menu          | `/start`    |
| `/help`     | Show help and tips      | `/help`     |
| `/status`   | Show all chain prices   | `/status`   |
| `/myalerts` | View your active alerts | `/myalerts` |

### 🎯 **Interactive Features**

- **Main Menu**: Navigate with inline buttons
- **Gas Tracking**: Select specific chains to monitor
- **Alert Setup**: Interactive chain selection and threshold input
- **Alert Management**: Delete alerts with one click
- **Real-time Updates**: Refresh gas prices instantly

## 🔧 Configuration

### Environment Variables (.env)

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
ETHERSCAN_API_KEY=your_etherscan_api_key
BSCSCAN_API_KEY=your_bscscan_api_key
POLYGONSCAN_API_KEY=your_polygonscan_api_key
```

### API Rate Limiting & Optimization

The bot is optimized to respect API rate limits while maintaining responsiveness:

- **Check Interval**: 2 minutes (30 times/hour instead of 360 times/hour)
- **Smart Scheduling**: Only checks chains where users have active alerts
- **API Efficiency**: Reduces unnecessary calls when no alerts exist
- **Free Tier Compatible**: Stays within Etherscan, BscScan, and PolygonScan free limits

**API Usage**: ~30 requests/hour vs previous 360 requests/hour (90% reduction!)

### Supported Chains

- **⚡ Ethereum (ETH)**: Chain ID 1
- **🟡 BSC**: Chain ID 56
- **🟣 Polygon**: Chain ID 137

### Gas Price Indicators

- **🟢 Low**: < 10 Gwei (Great for transactions)
- **🟡 Medium**: 10-50 Gwei (Normal usage)
- **🔴 High**: > 50 Gwei (Peak times)

## 🎨 User Interface Features

### **Visual Enhancements**

- **Chain Emojis**: ⚡ ETH, 🟡 BSC, 🟣 Polygon
- **Gas Price Emojis**: 🟢 Low, 🟡 Medium, 🔴 High
- **Rich Formatting**: Markdown support with bold text
- **Inline Keyboards**: Easy navigation without typing

### **Smart Alerts**

- **Decimal Support**: Set thresholds like 0.8, 1.5, 2.3 Gwei
- **Instant Notifications**: Get alerted when gas drops below your threshold
- **Alert Management**: View and delete alerts easily
- **Confirmation Messages**: Clear feedback when alerts are set

### **Real-time Monitoring**

- **2-Minute Updates**: Continuous background monitoring (respects API rate limits)
- **Multi-Chain**: Monitor all chains simultaneously
- **Status Overview**: See all chain prices at once
- **Refresh Function**: Get latest prices on demand
- **Smart Scheduling**: Only checks chains with active alerts to save API calls

## 🏗️ Project Structure

```
cross-chain-gasfee-tracker/
├── core/               # Main logic
│   ├── gas_tracker.py  # Multi-chain API interactions
│   ├── alert_manager.py # Smart alert processing
│   └── scheduler.py    # Background monitoring
├── bot/                # Telegram handlers
│   ├── command.py      # Rich command interface
│   └── bot_init.py     # Bot setup
├── data/               # Database files
├── config/             # API keys and constants
├── .env                # Environment variables
├── start.sh            # Easy startup script
└── main.py             # Entry point
```

## 🚀 Deployment

### Option 1: Easy Startup Script (Recommended)

```bash
./start.sh
```

### Option 2: Local Development

```bash
# Run in terminal
source .venv/bin/activate
python main.py
```

### Option 3: Background Process

```bash
# Run persistently using tmux
tmux new -s gasbot
source .venv/bin/activate
python main.py
# Ctrl+B then D to detach
```

### Option 4: Docker

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
   - Check your API key quotas

4. **Bot Not Responding**

   - Check if bot token is correct in .env
   - Verify bot is running: `ps aux | grep python`

5. **Decimal Thresholds Not Working**

   - Database supports decimals (REAL type)
   - Use values like 0.8, 1.5, 2.3 Gwei

### Logs

The bot provides real-time feedback:

- ✅ Database initialized
- ✅ Scheduler started
- ✅ Bot is running
- 🚨 Gas alerts sent
- ⚠️ API errors (handled automatically)

## 📊 Gas Price Examples

### **Setting Alerts**

- **Ethereum**: Set threshold to 0.8 Gwei (current: ~0.7 Gwei)
- **BSC**: Set threshold to 3.5 Gwei (current: ~3.2 Gwei)
- **Polygon**: Set threshold to 30 Gwei (current: ~25 Gwei)

### **Alert Triggers**

- When ETH gas drops from 0.8 to 0.7 Gwei → **Alert!** 🚨
- When BSC gas drops from 3.5 to 3.2 Gwei → **Alert!** 🚨
- When Polygon gas drops from 30 to 25 Gwei → **Alert!** 🚨

## 📈 Roadmap

- [ ] Add Solana and Avalanche support
- [ ] Implement gas fee predictions (AI)
- [ ] Create web dashboard for analytics
- [ ] Multi-language support
- [ ] Advanced alert types (time-based, trend-based)
- [ ] Push notifications to Discord/Slack
- [ ] Gas price forecasting
- [ ] MEV protection alerts

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
5. Check that your bot token is correct

## 🎉 What's New

### **Latest Updates**

- ✅ **Decimal Threshold Support**: Now supports 0.8, 1.5, 2.3 Gwei
- ✅ **Enhanced UI**: Rich emojis and visual indicators
- ✅ **Alert Management**: View and delete alerts easily
- ✅ **Multi-Chain Status**: See all chain prices at once
- ✅ **Better Error Handling**: Graceful API failure handling
- ✅ **Startup Script**: Easy one-command bot launch
- ✅ **API Optimization**: 2-minute intervals with smart scheduling (90% API reduction)
- ✅ **Rate Limit Compliance**: Respects free API tier limits

### **User Experience**

- 🎨 Beautiful interface with chain and gas price emojis
- 📱 Intuitive inline keyboard navigation
- 🔔 Smart alert confirmations with current price hints
- 📊 Real-time status overview for all chains
- 🗑️ One-click alert deletion
- 💡 Helpful tips and examples throughout

The bot is now production-ready with enterprise-grade features and a delightful user experience!
