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


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 View Current Gas Fees", callback_data="track_gas"),
            InlineKeyboardButton("📢 Set Gas Fee Alerts", callback_data="set_alert")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("📖 Help", callback_data="help")
        ]
    ])

def gas_chain_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Ethereum", callback_data="eth_track_gas")],
        [
            InlineKeyboardButton("BSC", callback_data="bsc_track_gas"),
            InlineKeyboardButton("Polygon", callback_data="matic_track_gas")
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
        [InlineKeyboardButton("🔍 Ethereum", callback_data="setalert_eth")],
        [
            InlineKeyboardButton("BSC", callback_data="setalert_bsc"),
            InlineKeyboardButton("Polygon", callback_data="setalert_matic")
        ],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ])


def format_gas_fee_message(chain_key: str, gas_fee: dict) -> str:
    chain_name = CHAIN_NAMES.get(chain_key, chain_key)
    return (
        f"Gas fees for *{chain_name}* (in wei per unit):\n"
        f"• Low: *{gas_fee['low']}*\n"
        f"• Medium: *{gas_fee['medium']}*\n"
        f"• High: *{gas_fee['high']}*"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command, show main menu."""
    if update.message:
        await update.message.reply_text(
            text=(
                f"👋 Welcome {update.effective_user.first_name} to the Cross-Chain Gas Fee Tracker!!\n"
                "Get real-time gas fee updates across *Ethereum*, *BSC*, and *Polygon*.\n"
                "Choose an option below to get started."
            ),
            reply_markup=main_menu_keyboard(),
            parse_mode='Markdown'
        )

async def show_gas_fee(query, chain_key: str):
    """Fetch and display gas fee for given chain"""
    try:
        chain_id = CHAIN_IDS[chain_key]
        gas_fee = get_gas_price(chain_id)
        text = format_gas_fee_message(chain_key, gas_fee)
    except Exception as e:
        text = f"Error fetching gas fee: {e}"
    await query.edit_message_text(text,reply_markup=back_refresh_keyboard(), parse_mode='Markdown')

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
    user_id= update.effective_user.id
    chat_id= update.effective_chat.id
    text = update.message.text
    chain = context.user_data.get("alert_chain")

    if not chain:
        return await update.message.reply_text("⚠️ Use /start and go through 'Set Gas Alert' first.")
    
    try:
        threshold = int(text)
    except ValueError:
        return await update.message.reply_text("❌ Please send a valid number (Gwei).")
    conn = sqlite3.connect("data/alerts.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO alerts (user_id, chat_id, chain, threshold, notified)
        VALUES (?, ?, ?, ?, 0)
    """, (user_id, chat_id, chain, threshold))
    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"✅ Alert set for *{CHAIN_NAMES[chain]}* when gas < {threshold} Gwei!",
        parse_mode="Markdown"
    )

    # Cleanup
    context.user_data.pop("alert_chain", None)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "track_gas":
        await query.edit_message_text(
            text="Select a chain to track:",
            reply_markup=gas_chain_keyboard(),
            parse_mode='Markdown'
        )
    elif query.data in ["eth_track_gas", "bsc_track_gas", "matic_track_gas"]:
        # Extract chain key
        key = query.data.split('_')[0]
        context.user_data["last_chain"]=key
        await show_gas_fee(query, key)
    elif query.data == "set_alert":
        await setalert(query)
    elif query.data.startswith("setalert_"):
        key = query.data.split("_")[1]
        context.user_data["alert_chain"] = key
        await query.edit_message_text(f"✍️ Send the Gwei threshold for *{CHAIN_NAMES[key]}*:", parse_mode="Markdown")
    elif query.data == "settings":
        await query.edit_message_text("⚙️ Here are your settings")
    elif query.data == "help":
        await query.edit_message_text("ℹ️ Here is your help section")
    elif query.data == "back_to_tracker":
        await query.edit_message_text(
            text="Select a chain to track:",
            reply_markup=gas_chain_keyboard(),
            parse_mode='Markdown'
        )
    elif query.data == "refresh":
        key = context.user_data.get("last_chain")
        if key:
            await show_gas_fee(query,key)
        else:
            await query.edit_message_text(
                "Could not refresh: missing chain info.\nPlease select a chain again.",
            reply_markup=gas_chain_keyboard(),
            parse_mode='Markdown'
            )
    elif query.data == 'back_to_menu':
        await query.edit_message_text(
            text=(
                f"👋 Welcome {update.effective_user.first_name} to the Cross-Chain Gas Fee Tracker!!\n"
                "Get real-time gas fee updates across *Ethereum*, *BSC*, and *Polygon*.\n"
                "Choose an option below to get started."
            ),
            reply_markup=main_menu_keyboard(),
            parse_mode='Markdown'
        )
    else:
        await query.edit_message_text("Unknown action.")

def register_handlers(app):
    """Register bot command and callback handlers."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gwei_input))
