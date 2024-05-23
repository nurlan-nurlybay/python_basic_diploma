# tg_API\core.py

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from log_config import logger
from site_API.core import SiteApi
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import html


class MyStates(StatesGroup):
    high_selected = State()
    low_selected = State()


class Bot:
    GREETING_TEXT = 'Hello! I will help you find the best movies and series.'
    INFO_TEXT = ('low - Returns a list of the worst movies/series.\n'
                 'high - Returns a list of mid movies/series.')
    DEFAULT_ERROR_TEXT = 'Sorry, I don’t understand you. The bot is still under development.'

    def __init__(self, token: str, site: SiteApi):
        state_storage = StateMemoryStorage()
        self.bot = TeleBot(token, state_storage=state_storage)
        self.site = site

    @classmethod
    def gen_inline_choice(cls):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Movies", callback_data="cb_movies"),
                   InlineKeyboardButton("Series", callback_data="cb_series"),
                   InlineKeyboardButton("Menu", callback_data="cb_menu"))
        return markup

    @classmethod
    def gen_num_choice(cls):
        markup = InlineKeyboardMarkup()
        markup.row_width = 5
        markup.add(InlineKeyboardButton("1", callback_data="1"),
                   InlineKeyboardButton("2", callback_data="2"),
                   InlineKeyboardButton("3", callback_data="3"),
                   InlineKeyboardButton("4", callback_data="4"),
                   InlineKeyboardButton("5", callback_data="5"),
                   InlineKeyboardButton("Menu", callback_data="cb_menu"))
        return markup

    @classmethod
    def gen_inline_menu(cls):
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("high", callback_data="cb_high"),
                   InlineKeyboardButton("low", callback_data="cb_low"))
        return markup

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'help', 'hello-world'])
        def send_welcome(message):
            self.bot.delete_message(message.chat.id, message.message_id)
            self.bot.send_message(message.chat.id, self.GREETING_TEXT)
            self.bot.send_message(message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())

        @self.bot.message_handler(regexp=r'привет|hello')
        def greet(message):
            self.bot.delete_message(message.chat.id, message.message_id)
            self.bot.send_message(message.chat.id, self.GREETING_TEXT)
            self.bot.send_message(message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_high"])
        def cb_high_handler(call):
            self.bot.set_state(call.from_user.id, MyStates.high_selected, call.message.chat.id)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.send_message(call.message.chat.id, "Movies/series?", reply_markup=self.gen_inline_choice())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_low"])
        def cb_low_handler(call):
            self.bot.set_state(call.from_user.id, MyStates.low_selected, call.message.chat.id)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.send_message(call.message.chat.id, "Movies/series?", reply_markup=self.gen_inline_choice())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_menu"])
        def cb_menu_handler(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.delete_state(call.message.from_user.id, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_movies", "cb_series"])
        def cb_choice_handler(call):
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            text = "How many {} would you like to find?\n(you may have to wait up to 20 seconds)"
            if call.data == "cb_movies":
                self.site.set_choice("movie")
                self.bot.send_message(call.message.chat.id, text=text.format("movies"),
                                      reply_markup=self.gen_num_choice())
            elif call.data == "cb_series":
                self.site.set_choice("series")
                self.bot.send_message(call.message.chat.id, text=text.format("series"),
                                      reply_markup=self.gen_num_choice())

        @self.bot.callback_query_handler(state=[MyStates.high_selected, MyStates.low_selected],
                                         func=lambda call: call.data in ["1", "2", "3", "4", "5"])
        def ask_limit_send_titles(call):
            msg_text: str = call.data
            if msg_text.isdigit():

                lim = int(msg_text)
                if lim <= 0:
                    lim = 1
                elif lim > 5:
                    lim = 5

                choice = 'MOVIES' if self.site.params["type"] == 'movie' else 'SERIES'
                state = str(self.bot.get_state(call.from_user.id, call.message.chat.id))

                if state == str(MyStates.high_selected):
                    response_json = self.site.get_high(lim)
                    self.bot.send_message(call.message.chat.id, f"TOP {lim} {choice}")
                elif state == str(MyStates.low_selected):
                    response_json = self.site.get_low(lim)
                    self.bot.send_message(call.message.chat.id, f"MID {lim} {choice}")
                else:
                    logger.exception('request without state')
                    response_json = self.site.get_high(lim)

                for i, title in enumerate(response_json["results"]):
                    description = html.unescape(f"{i + 1}. {title["title"]}\n\n"
                                                f"{title["synopsis"]}")
                    self.bot.send_photo(call.message.chat.id, photo=title["img"], caption=description)

                self.bot.send_message(call.message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())
            else:
                self.bot.send_message(call.message.chat.id, msg_text)

        @self.bot.message_handler(func=lambda message: True)
        def handle_default(message):
            self.bot.delete_message(message.chat.id, message.message_id)
            self.bot.reply_to(message, self.DEFAULT_ERROR_TEXT)

    def run(self):
        self.bot.add_custom_filter(custom_filters.StateFilter(self.bot))
        self.bot.add_custom_filter(custom_filters.IsDigitFilter())
        self.bot.infinity_polling(skip_pending=True)


'''
for some reason in cb_low_handler and cb_high_handler 
self.bot.set_state(call.from_user.id, MyStates.high_selected, call.message.chat.id)
this line of code has no effect. The states are never set.
'''