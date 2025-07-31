from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes, Application, CallbackQueryHandler
from core.gas_tracker import get_gas_price

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
        ]
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
    await query.edit_message_text(text, parse_mode='Markdown')

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
        await show_gas_fee(query, key)
    elif query.data == "set_alert":
        await query.edit_message_text("🚨 Gas tracking alert set!")
    elif query.data == "settings":
        await query.edit_message_text("⚙️ Here are your settings")
    elif query.data == "help":
        await query.edit_message_text("ℹ️ Here is your help section")
    else:
        await query.edit_message_text("Unknown action.")

def register_handlers(app: Application):
    """Register bot command and callback handlers."""
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
