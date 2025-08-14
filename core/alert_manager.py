from pathlib import Path
import sqlite3
from data.db import DB_PATH  
from core.gas_tracker import get_gas_price
from telegram import Bot
import asyncio

CHAIN_IDS = {
    'eth': 1,
    'bsc': 56,
    'matic': 137
}

def check_alerts_and_notify(bot: Bot):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, chat_id, chain, threshold FROM alerts WHERE notified = 0")
        alerts = cursor.fetchall()
        
        for alert_id, user_id, chat_id, chain, threshold in alerts:
            try:
                gas_data = get_gas_price(CHAIN_IDS[chain])
                
                # Check if gas_data contains an error
                if 'error' in gas_data:
                    print(f"API error for {chain}: {gas_data['error']}")
                    continue
                
                # Calculate current gas price (lowest of the three)
                current_gas_price = min(float(v) for v in gas_data.values())
                
                if current_gas_price <= threshold:
                    try:
                        # Use asyncio.run to run the async bot.send_message in a new event loop
                        asyncio.run(bot.send_message(
                            chat_id=chat_id,
                            text=(
                                f"🚨 *Gas Alert!*\n"
                                f"Chain: *{chain}*\n"
                                f"Current gas price: *{current_gas_price:.2f} Gwei*\n"
                                f"Threshold: *{threshold} Gwei*\n\n"
                                "You can adjust your alert in the menu below."
                            ),
                            parse_mode='Markdown'
                        ))
                        print(f"Alert sent successfully to chat {chat_id}")
                        
                        # Mark this alert as notified
                        cursor.execute("UPDATE alerts SET notified = 1 WHERE id = ?", (alert_id,))
                        conn.commit()
                        
                    except Exception as e:
                        print(f"Error sending message: {e}")
                        
            except (ValueError, KeyError) as e:
                print(f"Error processing gas data for {chain}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error for {chain}: {e}")
                continue
                
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
