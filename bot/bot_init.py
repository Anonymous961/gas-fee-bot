from telegram.ext import ApplicationBuilder, Application
from config.api_keys import config
from bot.command import register_handlers

bot = ApplicationBuilder().token(config["TELEGRAM_BOT_TOKEN"]).build()

register_handlers(bot)
