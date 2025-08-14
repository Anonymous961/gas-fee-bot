from apscheduler.schedulers.background import BackgroundScheduler
from core.alert_manager import check_alerts_and_notify
from telegram.ext import Application

def start_scheduler(app: Application):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: check_alerts_and_notify(app.bot), "interval", seconds=10)
    scheduler.start()
    print("✅ Scheduler started successfully!")

