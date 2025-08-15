from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from core.gas_tracker import get_gas_price
import sqlite3

# Use a dict for chain mapping
CHAIN_IDS = {
    'eth': 1,
    'bsc': 56,
    'matic': 137
}
CHAIN_NAMES = {
    'eth': 'Ethereum',
    'bsc': 'BSC',
    'matic': 'Polygon',
}
CHAIN_EMOJIS = {
    'eth': '⚡',
    'bsc': '🟡',
    'matic': '🟣',
}

def get_gas_emoji(gas_price):
    """Get emoji based on gas price (in Gwei)"""
    try:
        price = float(gas_price)
        if price < 10:
            return "🟢"  # Low
        elif price < 50:
            return "🟡"  # Medium
        else:
            return "🔴"  # High
    except:
        return "⚪"  # Unknown

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 View Current Gas Fees", callback_data="track_gas"),
            InlineKeyboardButton("📢 Set Gas Fee Alerts", callback_data="set_alert")
        ],
        [
            InlineKeyboardButton("📊 Gas Status", callback_data="gas_status"),
            InlineKeyboardButton("📢 My Alerts", callback_data="my_alerts")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ])

def gas_chain_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{CHAIN_EMOJIS['eth']} Ethereum", callback_data="eth_track_gas")],
        [
            InlineKeyboardButton(f"{CHAIN_EMOJIS['bsc']} BSC", callback_data="bsc_track_gas"),
            InlineKeyboardButton(f"{CHAIN_EMOJIS['matic']} Polygon", callback_data="matic_track_gas")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ])

def back_refresh_keyboard():
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🔁 Refresh", callback_data="refresh"),
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_tracker")
        ]]
    )

def setalert_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{CHAIN_EMOJIS['eth']} Ethereum", callback_data="setalert_eth")],
        [
            InlineKeyboardButton(f"{CHAIN_EMOJIS['bsc']} BSC", callback_data="setalert_bsc"),
            InlineKeyboardButton(f"{CHAIN_EMOJIS['matic']} Polygon", callback_data="setalert_matic")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ])

def format_gas_fee_message(chain_key: str, gas_fee: dict) -> str:
    chain_name = CHAIN_NAMES.get(chain_key, chain_key)
    chain_emoji = CHAIN_EMOJIS.get(chain_key, "🔗")
    
    # Add emojis to gas prices
    low_emoji = get_gas_emoji(gas_fee['low'])
    medium_emoji = get_gas_emoji(gas_fee['medium'])
    high_emoji = get_gas_emoji(gas_fee['high'])
    
    return (
        f"{chain_emoji} *{chain_name}* Gas Fees (in Gwei):\n\n"
        f"{low_emoji} Low: *{gas_fee['low']}*\n"
        f"{medium_emoji} Medium: *{gas_fee['medium']}*\n"
        f"{high_emoji} High: *{gas_fee['high']}*"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command, show main menu."""
    if update.message:
        await update.message.reply_text(
            text=(
                f"👋 Welcome {update.effective_user.first_name} to the Cross-Chain Gas Fee Tracker!!\n\n"
                "⚡ Get real-time gas fee updates across *Ethereum*, *BSC*, and *Polygon*.\n"
                "📢 Set custom alerts and get notified when gas prices drop!\n\n"
                "Choose an option below to get started:"
            ),
            reply_markup=main_menu_keyboard(),
            parse_mode='Markdown'
        )

async def myalerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myalerts command - show user's active alerts"""
    user_id = update.effective_user.id
    
    try:
        conn = sqlite3.connect("data/alerts.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, chain, threshold, notified 
            FROM alerts 
            WHERE user_id = ? AND notified = 0
            ORDER BY chain, threshold
        """, (user_id,))
        alerts = cursor.fetchall()
        conn.close()
        
        if not alerts:
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    "📭 *No Active Alerts*\n\n"
                    "You don't have any active gas price alerts.\n"
                    "Use the menu to set up your first alert!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
                    ]]),
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    "📭 *No Active Alerts*\n\n"
                    "You don't have any active gas price alerts.\n"
                    "Use /start to set up your first alert!",
                    parse_mode='Markdown'
                )
            return
        
        # Group alerts by chain
        alerts_by_chain = {}
        for alert_id, chain, threshold, notified in alerts:
            if chain not in alerts_by_chain:
                alerts_by_chain[chain] = []
            alerts_by_chain[chain].append((alert_id, threshold))
        
        # Format the message
        message = "📢 *Your Active Gas Price Alerts*\n\n"
        
        for chain, chain_alerts in alerts_by_chain.items():
            chain_emoji = CHAIN_EMOJIS.get(chain, "🔗")
            chain_name = CHAIN_NAMES.get(chain, chain)
            
            message += f"{chain_emoji} *{chain_name}*\n"
            for alert_id, threshold in chain_alerts:
                message += f"   • Alert when gas < {threshold} Gwei\n"
            message += "\n"
        
        message += "💡 *Tip:* Alerts are automatically removed after they're triggered."
        
        # Create keyboard with delete options
        keyboard = []
        for alert_id, chain, threshold, notified in alerts:
            chain_emoji = CHAIN_EMOJIS.get(chain, "🔗")
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ Delete {chain_emoji} {threshold} Gwei", 
                    callback_data=f"delete_alert_{alert_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                text=message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
    except Exception as e:
        error_msg = f"❌ Error fetching alerts: {e}"
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=error_msg,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
                ]]),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Error fetching alerts: {e}",
                parse_mode='Markdown'
            )

async def delete_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a specific alert"""
    query = update.callback_query
    await query.answer()
    
    try:
        alert_id = int(query.data.split('_')[2])
        user_id = query.from_user.id
        
        conn = sqlite3.connect("data/alerts.db")
        cursor = conn.cursor()
        
        # Verify the alert belongs to the user and delete it
        cursor.execute("""
            DELETE FROM alerts 
            WHERE id = ? AND user_id = ? AND notified = 0
        """, (alert_id, user_id))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            await query.edit_message_text(
                "✅ *Alert Deleted Successfully!*\n\n"
                "The gas price alert has been removed.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
                ]]),
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ *Alert Not Found*\n\n"
                "The alert may have already been deleted or triggered.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
                ]]),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        await query.edit_message_text(
            f"❌ *Error Deleting Alert*\n\n{str(e)}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
            ]]),
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "🤖 *Cross-Chain Gas Fee Tracker Bot Help*\n\n"
        "*Commands:*\n"
        "• `/start` - Show main menu\n"
        "• `/help` - Show this help message\n"
        "• `/status` - Show current gas prices for all chains\n"
        "• `/myalerts` - View your active alerts\n\n"
        "*Features:*\n"
        "• 🔍 View real-time gas fees\n"
        "• 📢 Set custom price alerts\n"
        "• 📊 Monitor multiple chains\n"
        "• ⚡ Get instant notifications\n\n"
        "*Gas Price Indicators:*\n"
        "🟢 Low (< 10 Gwei)\n"
        "🟡 Medium (10-50 Gwei)\n"
        "🔴 High (> 50 Gwei)\n\n"
        "*Supported Chains:*\n"
        "⚡ Ethereum (ETH)\n"
        "🟡 BSC (BNB)\n"
        "🟣 Polygon (MATIC)\n\n"
        "*Quick Tips:*\n"
        "• Set alerts for off-peak hours when gas is typically lower\n"
        "• Use the Status command to compare gas across all chains\n"
        "• Refresh gas prices to get the latest data\n"
        "• All gas prices are displayed in Gwei (not wei)\n"
        "• You can set decimal thresholds like 0.8 Gwei"
    )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=help_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
            ]]),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=help_text,
            parse_mode='Markdown'
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show current gas prices for all chains"""
    status_text = "📊 *Current Gas Fee Status*\n\n"
    
    for chain_key, chain_name in CHAIN_NAMES.items():
        try:
            chain_id = CHAIN_IDS[chain_key]
            gas_data = get_gas_price(chain_id)
            chain_emoji = CHAIN_EMOJIS[chain_key]
            
            if 'error' not in gas_data:
                current_gas = min(float(v) for v in gas_data.values())
                gas_emoji = get_gas_emoji(current_gas)
                status_text += f"{chain_emoji} *{chain_name}*: {gas_emoji} *{current_gas:.2f} Gwei*\n"
            else:
                status_text += f"{chain_emoji} *{chain_name}*: ⚠️ API Error\n"
        except Exception as e:
            status_text += f"{CHAIN_EMOJIS[chain_key]} *{chain_name}*: ❌ Error\n"
    
    status_text += "\n🟢 Low | 🟡 Medium | 🔴 High"
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=status_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")
            ]]),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=status_text,
            parse_mode='Markdown'
        )

async def show_gas_fee(query, chain_key: str):
    """Fetch and display gas fee for given chain"""
    try:
        chain_id = CHAIN_IDS[chain_key]
        gas_data = get_gas_price(chain_id)
        text = format_gas_fee_message(chain_key, gas_data)
    except Exception as e:
        text = f"❌ Error fetching gas fee: {e}"
    await query.edit_message_text(text, reply_markup=back_refresh_keyboard(), parse_mode='Markdown')

async def setalert(query):
    await query.edit_message_text("🪙 Choose a chain:", reply_markup=setalert_keyboard())

async def send_gas_alert(bot, chat_id: int, chain: str, current_gas_price: float, threshold: float):
    """Send a gas alert to a specific user"""
    await bot.send_message(
        chat_id=chat_id,
        text=(
            f"🚨 *Gas Alert!*\n"
            f"Chain: *{chain}*\n"
            f"Current gas price: *{current_gas_price:.2f} Gwei*\n"
            f"Threshold: *{threshold} Gwei*\n\n"
            "You can adjust your alert in the menu below."
        ),
        parse_mode='Markdown'
    )

async def handle_gwei_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text
    chain = context.user_data.get("alert_chain")

    if not chain:
        return await update.message.reply_text("⚠️ Use /start and go through 'Set Gas Alert' first.")
    
    try:
        # Allow decimal values (like 0.8 Gwei)
        threshold = float(text)
        if threshold <= 0:
            return await update.message.reply_text("❌ Please send a valid positive number (Gwei).")
        if threshold > 1000:
            return await update.message.reply_text("❌ Threshold seems too high. Please send a reasonable value in Gwei (e.g., 0.5, 5, 50).")
    except ValueError:
        return await update.message.reply_text("❌ Please send a valid number (Gwei). You can use decimals like 0.8.")
    
    conn = sqlite3.connect("data/alerts.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO alerts (user_id, chat_id, chain, threshold, notified)
        VALUES (?, ?, ?, ?, 0)
    """, (user_id, chat_id, chain, threshold))
    conn.commit()
    conn.close()

    chain_emoji = CHAIN_EMOJIS.get(chain, "🔗")
    chain_name = CHAIN_NAMES.get(chain, chain)
    
    # Format threshold display based on value
    if threshold < 1:
        threshold_display = f"{threshold:.3f}"
    elif threshold < 10:
        threshold_display = f"{threshold:.2f}"
    else:
        threshold_display = f"{threshold:.1f}"
    
    await update.message.reply_text(
        f"✅ *Alert Set Successfully!*\n\n"
        f"{chain_emoji} Chain: *{chain_name}*\n"
        f"📊 Threshold: *{threshold_display} Gwei*\n\n"
        f"I'll notify you when {chain_name} gas drops below {threshold_display} Gwei! 🚨\n\n"
        f"💡 *Current {chain_name} gas: ~0.7 Gwei* (use /status to check)",
        parse_mode="Markdown"
    )

    # Cleanup
    context.user_data.pop("alert_chain", None)
    
ADMIN_IDS = [1152109549]
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only command to show bot statistics"""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("🚫 This command is for admins only.")
        return
    
    try:
        conn = sqlite3.connect("data/alerts.db")
        cursor = conn.cursor()
        
        # Get user count
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM alerts")
        user_count = cursor.fetchone()[0]
        
        # Get alert counts
        cursor.execute("SELECT COUNT(*) FROM alerts")
        total_alerts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE notified = 1")
        triggered_alerts = cursor.fetchone()[0]
        
        # Get chain distribution
        cursor.execute("""
            SELECT chain, COUNT(*) as count 
            FROM alerts 
            GROUP BY chain
        """)
        chain_stats = cursor.fetchall()
        
        conn.close()
        
        # Format message
        message = (
            "📊 *Bot Statistics*\n\n"
            f"👥 Total Users: *{user_count}*\n"
            f"🔔 Total Alerts: *{total_alerts}*\n"
            f"🚨 Triggered Alerts: *{triggered_alerts}*\n\n"
            "*Chain Distribution:*\n"
        )
        
        for chain, count in chain_stats:
            chain_emoji = CHAIN_EMOJIS.get(chain, "🔗")
            chain_name = CHAIN_NAMES.get(chain, chain)
            message += f"{chain_emoji} {chain_name}: *{count} alerts*\n"
        
        await update.message.reply_text(
            text=message,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error fetching stats: {str(e)}",
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "track_gas":
        await query.edit_message_text(
            text="🔍 Select a chain to track:",
            reply_markup=gas_chain_keyboard(),
            parse_mode='Markdown'
        )
    elif query.data in ["eth_track_gas", "bsc_track_gas", "matic_track_gas"]:
        # Extract chain key
        key = query.data.split('_')[0]
        context.user_data["last_chain"] = key
        await show_gas_fee(query, key)
    elif query.data == "set_alert":
        await setalert(query)
    elif query.data.startswith("setalert_"):
        key = query.data.split("_")[1]
        context.user_data["alert_chain"] = key
        chain_emoji = CHAIN_EMOJIS.get(key, "🔗")
        chain_name = CHAIN_NAMES.get(key, key)
        await query.edit_message_text(
            f"✍️ Send the Gwei threshold for {chain_emoji} *{chain_name}*:\n\n"
            f"*Examples:*\n"
            f"• Send `0.8` to get alerted when gas < 0.8 Gwei\n"
            f"• Send `5` to get alerted when gas < 5 Gwei\n"
            f"• Send `50` to get alerted when gas < 50 Gwei\n\n"
            f"💡 *Current {chain_name} gas: ~0.7 Gwei*",
            parse_mode="Markdown"
        )
    elif query.data == "gas_status":
        await status_command(update, context)
    elif query.data == "my_alerts":
        await myalerts_command(update, context)
    elif query.data.startswith("delete_alert_"):
        await delete_alert(update, context)
    elif query.data == "help":
        await help_command(update, context)
    elif query.data == "back_to_tracker":
        await query.edit_message_text(
            text="🔍 Select a chain to track:",
            reply_markup=gas_chain_keyboard(),
            parse_mode='Markdown'
        )
    elif query.data == "refresh":
        key = context.user_data.get("last_chain")
        if key:
            await show_gas_fee(query, key)
        else:
            await query.edit_message_text(
                "Could not refresh: missing chain info.\nPlease select a chain again.",
                reply_markup=gas_chain_keyboard(),
                parse_mode='Markdown'
            )
    elif query.data == 'back_to_menu':
        await query.edit_message_text(
            text=(
                f"👋 Welcome {update.effective_user.first_name} to the Cross-Chain Gas Fee Tracker!!\n\n"
                "⚡ Get real-time gas fee updates across *Ethereum*, *BSC*, and *Polygon*.\n"
                "📢 Set custom alerts and get notified when gas prices drop!\n\n"
                "Choose an option below to get started:"
            ),
            reply_markup=main_menu_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("❓ Unknown action.")

def register_handlers(app):
    """Register bot command and callback handlers."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("myalerts", myalerts_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gwei_input))
