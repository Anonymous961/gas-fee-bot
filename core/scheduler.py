from apscheduler.schedulers.background import BackgroundScheduler
from core.alert_manager import check_alerts_and_notify
from telegram.ext import Application
import time

def start_scheduler(app: Application):
    """
    Start the background scheduler for gas price monitoring.
    Uses 2-minute intervals to respect API rate limits.
    """
    scheduler = BackgroundScheduler()
    
    # Check every 2 minutes instead of 10 seconds to respect API rate limits
    # This gives us 30 requests per hour instead of 360 requests per hour
    scheduler.add_job(
        lambda: check_alerts_and_notify(app.bot), 
        "interval", 
        minutes=2,
        id="gas_price_check",
        name="Gas Price Alert Check"
    )
    
    scheduler.start()
    print("✅ Scheduler started successfully!")
    print("📊 Checking gas prices every 2 minutes (30 times/hour)")
    print("💡 This respects API rate limits while maintaining responsiveness")

