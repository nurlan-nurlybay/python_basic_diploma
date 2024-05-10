from config import AppSettings
from tg_API.core import Bot


def main():
    app = AppSettings()
    bot = Bot(app.bot_token.get_secret_value())
    bot.setup_handlers()
    bot.run()


if __name__ == '__main__':
    main()
