from bot.bot_init import bot
from data.db import init_db
from core.scheduler import start_scheduler
import threading
import time

def start_scheduler_delayed():
    """Start the scheduler after a short delay to ensure the bot is running"""
    time.sleep(2)  # Wait for bot to start
    start_scheduler(bot)

def main():
    try:
        print("🚀 Starting Cross-Chain Gas Fee Tracker Bot...")
        init_db()
        print("✅ Database initialized")
        
        print("⏰ Starting background scheduler...")
        scheduler_thread = threading.Thread(target=start_scheduler_delayed, daemon=True)
        scheduler_thread.start()
        
        print("🤖 Starting Telegram bot...")
        print("🎯 Bot is now running! Press Ctrl+C to stop.")
        bot.run_polling()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        raise

if __name__ == "__main__":
    main()
