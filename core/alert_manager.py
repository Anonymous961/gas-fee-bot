from pathlib import Path
import sqlite3
from data.db import DB_PATH  


def check_alerts_and_notify(bot):
    print(f"Connecting to DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("check alert")
    cursor.execute("SELECT id, user_id, chat_id, chain, threshold FROM alerts WHERE notified = 0")
    alerts = cursor.fetchall()
    print(alerts)
    conn.close()
