from config.api_keys import config

def main():
    print(config["TELEGRAM_BOT_TOKEN"])


if __name__ == "__main__":
    main()