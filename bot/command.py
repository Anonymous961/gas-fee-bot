from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes, Application, CallbackQueryHandler
from core.gas_tracker import eth_gas_tracker

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start handle with the main features"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 View Current Gas Fees", callback_data="track_gas"),InlineKeyboardButton("📢 Set Gas Fee Alerts", callback_data="set_alert")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings"),InlineKeyboardButton("📖 Help", callback_data="help")]
    ])

    await update.message.reply_text(
        text=f"👋 Welcome {update.effective_user.first_name} to the Cross-Chain Gas Fee Tracker!!\nGet real-time gas fee updates across *Ethereum*, *BSC*, and *Polygon*.\nChoose an option below to get started.",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def track_gas_buttton_handler(query,get_eth_price):
    gas_fee=get_eth_price()
    
    message = (
        "Current gas fees (in wei per unit of gas):\n"
        f"• Low: *{gas_fee['low']}*\n"
        f"• Medium: *{gas_fee['medium']}*\n"
        f"• High: *{gas_fee['high']}*"
    )
    await query.edit_message_text(message,parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query= update.callback_query
    await query.answer()

    if query.data == "track_gas":
        await track_gas_buttton_handler(query,eth_gas_tracker)
    elif query.data == "set_alert":
        await query.edit_message_text("Gas tracking alert set")
    elif query.data == "settings":
        await query.edit_message_text("Here is your settings")
    elif query.data == "help":
        await query.edit_message_text("Here is your help")

def register_handlers(app: Application):
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CallbackQueryHandler(button_handler))