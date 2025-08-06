from bot.bot_init import bot
from data.db import init_db
from core.scheduler import start_scheduler

def main():
    init_db()
    print("Starting the bot....")
    start_scheduler(bot)
    bot.run_polling()

if __name__ == "__main__":
    main()
