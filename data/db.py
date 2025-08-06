from pathlib import Path
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "alerts.db")

def init_db():
    print(f"Using DB path: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    print("db connection successful")
    print("creating alerts table")
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            chain TEXT,
            threshold INTEGER,
            notified INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
