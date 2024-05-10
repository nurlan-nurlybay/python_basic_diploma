#tg_API-core.py

import re
from telebot import TeleBot


class Bot:
    WELCOME_TEXT = "Hello world!"
    GREETING_TEXT = 'Здравствуйте!'
    DEFAULT_ERROR_TEXT = 'Извините, я вас не понимаю. Бот еще в стадии разработки.'

    def __init__(self, token):
        self.bot = TeleBot(token)

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'help', 'hello-world'])
        def send_welcome(message):
            self.bot.reply_to(message, self.WELCOME_TEXT)

        @self.bot.message_handler(func=lambda message: re.match(r'привет', message.text, re.IGNORECASE))
        def greet(message):
            self.bot.reply_to(message, self.GREETING_TEXT)

        @self.bot.message_handler(func=lambda message: True)
        def handle_default(message):
            self.bot.reply_to(message, self.DEFAULT_ERROR_TEXT)

    def run(self):
        self.bot.infinity_polling()

