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

def get_active_chains():
    """Get list of chains that have active alerts to avoid unnecessary API calls"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT chain 
            FROM alerts 
            WHERE notified = 0
        """)
        active_chains = [row[0] for row in cursor.fetchall()]
        conn.close()
        return active_chains
    except Exception as e:
        print(f"Error getting active chains: {e}")
        return []

def check_alerts_and_notify(bot: Bot):
    """
    Check all active alerts and send notifications when gas prices drop below thresholds.
    All gas prices are in Gwei (not wei).
    Only checks chains where users have active alerts to save API calls.
    """
    try:
        # Get chains with active alerts to avoid unnecessary API calls
        active_chains = get_active_chains()
        if not active_chains:
            print("💤 No active alerts - skipping gas price check")
            return
        
        print(f"🔍 Checking gas prices for chains with active alerts: {', '.join(active_chains)}")
        
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
                
                # Calculate current gas price (lowest of the three) - all values are in Gwei
                try:
                    current_gas_price = min(float(v) for v in gas_data.values())
                except (ValueError, TypeError) as e:
                    print(f"Error parsing gas price for {chain}: {e}, data: {gas_data}")
                    continue
                
                print(f"Chain: {chain}, Current: {current_gas_price:.3f} Gwei, Threshold: {threshold} Gwei")
                
                # Compare Gwei to Gwei (both are in the same unit)
                if current_gas_price <= threshold:
                    try:
                        # Use asyncio.run to run the async bot.send_message in a new event loop
                        asyncio.run(bot.send_message(
                            chat_id=chat_id,
                            text=(
                                f"🚨 *Gas Alert!*\n"
                                f"Chain: *{chain.upper()}*\n"
                                f"Current gas price: *{current_gas_price:.3f} Gwei*\n"
                                f"Threshold: *{threshold} Gwei*\n\n"
                                f"✅ Gas price is now below your {threshold} Gwei threshold!\n"
                                "You can adjust your alerts in the menu below."
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
