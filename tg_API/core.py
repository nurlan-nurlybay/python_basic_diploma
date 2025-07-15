# tg_API\core.py

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from log_config import logger
from site_API.core import SiteApi
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from database.common.models import History
from database.core import db_manage, db
import html


class MyStates(StatesGroup):
    """
    Represents the different states a user can be in within the bot's conversation logic.
    """
    high_selected = State()
    low_selected = State()
    custom_selected = State()
    custom_low_set = State()
    custom_high_set = State()


class Bot:
    """
    A Telegram bot that assists users in finding the best movies and series based on various criteria.

    Attributes:
        GREETING_TEXT (str): Initial greeting message presented to users.
        INFO_TEXT (str): Information about the available bot commands.
        DEFAULT_ERROR_TEXT (str): Default error message for unrecognized commands.
        oneFive (list of str): Quick reference list containing the numbers 1 through 5 for command choices.
        oneTen (list of str): Quick reference list containing the numbers 1 through 10 for command choices.
    """
    GREETING_TEXT = 'Hello! I will help you find the best movies and series.'
    INFO_TEXT = ('[low] - Returns a list of bad movies/series.\n'
                 '[high] - Returns a list of the best movies/series.\n'
                 '[custom] - Allow to specify a rating range.\n'
                 '[history] - Last 5 requests.')
    DEFAULT_ERROR_TEXT = 'Sorry, I don’t understand you. The bot is still under development.'

    oneFive = ["1", "2", "3", "4", "5"]
    oneTen = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

    def __init__(self, token: str, site: SiteApi):
        """
        Initialize the bot with necessary configurations.

        :param token: Telegram API token provided by BotFather.
        :param site: Instance of SiteApi to interact with movie data.
        """
        state_storage = StateMemoryStorage()
        self.bot = TeleBot(token, state_storage=state_storage)
        self.site = site

    @staticmethod
    def trim_user_history():
        """
        Trims the user history in the database to maintain only the latest 5 entries per user.
        :return:
        """

        # Query to find all user_ids in the history
        user_ids = History.select(History.user_id).distinct()

        # Loop through each user and trim their history
        for user_id in user_ids:
            # Find the IDs of the latest 10 records for the user
            latest_ids = (History.select(History.id)
                          .where(History.user_id == user_id.user_id)
                          .order_by(History.created_at.desc())
                          .limit(5))

            # Delete all records for this user that are not in the latest 10
            (History
             .delete()
             .where((History.user_id == user_id.user_id) & (History.id.not_in(latest_ids)))
             .execute())

    @staticmethod
    def log_user_action(user_id, action, response=None):
        """
        Logs user actions and their responses to the database.

        :param user_id: The user ID from Telegram.
        :param action: The action performed by the user.
        :param response: The response from the bot to the action, optional.
        """
        db_manage.store(db, History, [{"user_id": user_id, "action": action, "response": response}])

    @staticmethod
    def get_user_history(user_id):
        """
        Retrieves formatted user history for display.

        :param user_id: The user ID from Telegram.
        :return: Formatted history string for display.
        """
        return db_manage.retrieve(History, History.user_id == user_id, order_by=[History.created_at.desc()], limit=5)

    def format_history_for_display(self, user_id):
        """
        Formats the user's action history for display.

        :param user_id: The user ID from Telegram.
        :return: A string that represents the formatted user history.
        """
        history_records = self.get_user_history(user_id)
        history_list = []
        for index, record in enumerate(history_records, start=1):
            entry = f"{index}. {record.action}\n{html.unescape(record.response)}"
            history_list.append(entry)
        return "\n".join(history_list) if history_list else "No history available."

    @classmethod
    def gen_type_choice(cls):
        """
        Generates an inline keyboard with choices between 'Movies' and 'Series'.

        :return: The markup for the inline keyboard.
        """
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("Movies", callback_data="cb_movies"),
                   InlineKeyboardButton("Series", callback_data="cb_series"),
                   InlineKeyboardButton("Menu", callback_data="cb_menu"))
        return markup

    @classmethod
    def gen_limit_choice(cls):
        """
        Generates an inline keyboard for selecting the number of movies or series a user wants to retrieve.

        :return: InlineKeyboardMarkup object with number options and a menu button.
        """
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
    def gen_rating_choice(cls):
        """
        Generates an inline keyboard to set the boundaries for custom movie/series rating searches.

        :return: InlineKeyboardMarkup object for selecting ratings from 1 to 10.
        """
        markup = InlineKeyboardMarkup()
        markup.row_width = 5
        markup.add(InlineKeyboardButton("1", callback_data="1"),
                   InlineKeyboardButton("2", callback_data="2"),
                   InlineKeyboardButton("3", callback_data="3"),
                   InlineKeyboardButton("4", callback_data="4"),
                   InlineKeyboardButton("5", callback_data="5"),
                   InlineKeyboardButton("6", callback_data="6"),
                   InlineKeyboardButton("7", callback_data="7"),
                   InlineKeyboardButton("8", callback_data="8"),
                   InlineKeyboardButton("9", callback_data="9"),
                   InlineKeyboardButton("10", callback_data="10"),
                   InlineKeyboardButton("Menu", callback_data="cb_menu"))
        return markup

    @classmethod
    def gen_inline_menu(cls):
        """
        Generates the main menu as an inline keyboard that includes options for high, low, custom searches, and history.

        :return: InlineKeyboardMarkup object for the main command menu.
        """
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton("high", callback_data="cb_high"),
                   InlineKeyboardButton("low", callback_data="cb_low"),
                   InlineKeyboardButton("custom", callback_data="cb_custom"),
                   InlineKeyboardButton("history", callback_data="cb_history"))
        return markup

    @classmethod
    def gen_numeric_choice(cls, start, end, callback_prefix):
        """
        Generates a dynamic numeric choice inline keyboard ranging from 'start' to 'end'.

        :param start: The starting number for the button range.
        :param end: The ending number for the button range.
        :param callback_prefix: Prefix for callback data associated with each button.
        :return: InlineKeyboardMarkup with numbered buttons and a menu return button.
        """
        markup = InlineKeyboardMarkup(row_width=5)
        buttons = [InlineKeyboardButton(str(i), callback_data=f"{callback_prefix}_{i}") for i in range(start, end + 1)]
        buttons.append(InlineKeyboardButton("Menu", callback_data="cb_menu"))
        markup.add(*buttons)
        return markup

    def setup_handlers(self):
        """
        Configures and registers the message and callback query handlers for the Telegram bot.
        This method organizes the response behavior for various commands and user interactions.

        (call this method in main before you call the run() method)

        :return: None
        """

        @self.bot.message_handler(commands=['start', 'help', 'hello-world'])
        def send_welcome(message):
            """
            Sends a welcome message along with the main command menu when the user starts the bot or asks for help.

            :param message: The message object containing user and chat details.
            :return: None
            """
            self.bot.delete_message(message.chat.id, message.message_id)
            self.bot.send_message(message.chat.id, self.GREETING_TEXT)
            self.bot.send_message(message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())

        @self.bot.message_handler(regexp=r'привет|hello')
        def greet(message):
            """
            Sends a greeting message similar to the welcome message when the user sends a greeting.

            :param message: The message object from the user containing the greeting.
            :return: None
            """
            self.bot.delete_message(message.chat.id, message.message_id)
            self.bot.send_message(message.chat.id, self.GREETING_TEXT)
            self.bot.send_message(message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_high"])
        def cb_high_handler(call):
            """
            Handles the selection of the 'high' rating option by the user.
            This method sets the bot state to 'high_selected', deletes the previous inline message,
            and prompts the user to choose between movies or series.

            :param call: The callback query from Telegram.
            """
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.set_state(call.from_user.id, MyStates.high_selected, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, "Movies/series?", reply_markup=self.gen_type_choice())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_low"])
        def cb_low_handler(call):
            """
            Responds to the user's selection of the 'low' rating option. It sets the bot state to 'low_selected',
            deletes the previous message, and prompts for the type of content (movies or series).

            :param call: The callback query from Telegram.
            """
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.set_state(call.from_user.id, MyStates.low_selected, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, "Movies/series?", reply_markup=self.gen_type_choice())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_custom"])
        def cb_custom_handler(call):
            """
            Activates when the user selects the 'custom' option, allowing them to specify custom search criteria.
            This sets the state to 'custom_selected' and prompts for the type of content.

            :param call: The callback query from Telegram.
            """
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.set_state(call.from_user.id, MyStates.custom_selected, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, "Movies/series?", reply_markup=self.gen_type_choice())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_history"])
        def cb_history_handler(call):
            """
            Displays the user's history upon selection of the 'history' option from the menu.
            It retrieves the user's previous interactions and formats them for display.

            :param call: The callback query from Telegram.
            """
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            history_text = self.format_history_for_display(call.from_user.id)
            self.bot.send_message(call.message.chat.id, 'HISTORY')
            self.bot.send_message(call.message.chat.id, history_text)
            self.bot.send_message(call.message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_menu"])
        def cb_menu_handler(call):
            """
            Handles the menu command from any inline keyboard interaction, clearing any current state
            and showing the main command menu again.

            :param call: The callback query from Telegram.
            """
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.delete_state(call.from_user.id, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())

        @self.bot.callback_query_handler(func=lambda call: call.data in ["cb_movies", "cb_series"])
        def cb_choice_handler(call):
            """
            Responds to the user's selection of either 'Movies' or 'Series' from the type choice menu.
            This method updates the user's choice in the site API, deletes the previous message,
            and prompts the user to specify the number of titles they want to find, providing an
            appropriate inline keyboard for selection.

            :param call: The callback query from Telegram, containing the user's choice.
            """
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            text = "How many {} would you like to find?\n(you may have to wait up to 20 seconds)"
            if call.data == "cb_movies":
                self.site.set_choice("movie")
                self.bot.send_message(call.message.chat.id, text=text.format("movies"),
                                      reply_markup=self.gen_limit_choice())
            elif call.data == "cb_series":
                self.site.set_choice("series")
                self.bot.send_message(call.message.chat.id, text=text.format("series"),
                                      reply_markup=self.gen_limit_choice())

        @self.bot.callback_query_handler(state=[MyStates.high_selected, MyStates.low_selected],
                                         func=lambda call: call.data in self.oneFive)
        def cb_limit_handler_send_high_low(call):
            """
            Handles user responses after selecting the type of content (movies or series) and the number of titles they want to fetch.
            This method determines if the user's query should fetch high or low rated titles based on the previously set state.
            It retrieves the requested titles from the API, sends them to the user, and logs the interaction. After sending the data,
            it cleans up by deleting the previous messages and states and then returns the user to the main menu.

            :param call: The callback query from Telegram, containing the user's numeric choice which specifies the number of titles.
            """
            self.site.set_lim(call.data)
            choice = 'MOVIES' if self.site.params["type"] == 'movie' else 'SERIES'
            state = str(self.bot.get_state(call.from_user.id, call.message.chat.id))
            req = None

            if state == str(MyStates.high_selected):
                response_json = self.site.get_high()
                req = 'TOP'
            elif state == str(MyStates.low_selected):
                response_json = self.site.get_low()
                req = 'MID'
            else:
                logger.exception('request without state')
                response_json = self.site.get_high()
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.send_message(call.message.chat.id, "{} {} {}".format(req, call.data, choice))

            titles = ''
            if "results" in response_json:
                for i, title in enumerate(response_json["results"]):
                    description = html.unescape(f"{i + 1}. {title['title']}\n\n"
                                                f"{title['synopsis']}\n\n"
                                                f"imdbrating: {title['imdbrating']}")
                    self.bot.send_photo(call.message.chat.id, photo=title["img"], caption=description)
                    titles += f"{title['title']}\n"
            else:
                self.bot.send_message(call.message.chat.id, text="no results")

            self.bot.delete_state(call.from_user.id, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())
            self.log_user_action(call.from_user.id,
                                 "{} {} {}".format(req, call.data, choice), titles)

        @self.bot.callback_query_handler(state=MyStates.custom_selected,
                                         func=lambda call: call.data in self.oneFive)
        def cb_limit_handler_set_custom_low(call):
            """
            Responds to user input selecting a custom search limit for movies or series after they tap custom.
            This method sets the low boundary for the custom search based on the user's selection.
            After setting the low boundary, it prompts the user to set the high boundary by displaying
            the appropriate rating choice options.

            :param call: The callback query from Telegram, which includes the user's selection for the number of results they desire.
            """
            self.site.set_lim(call.data)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.set_state(call.from_user.id, MyStates.custom_low_set, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, "Set low:", reply_markup=self.gen_rating_choice())

        @self.bot.callback_query_handler(state=MyStates.custom_low_set,
                                         func=lambda call: call.data in self.oneTen)
        def cb_rating_handler_set_custom_high(call):
            """
            Responds to user input after setting the low boundary for a custom search.
            This method sets the high boundary for the custom rating range based on the user's selection.
            It prompts the user to confirm the high boundary, preparing to execute the search with the defined limits.

            :param call: The callback query from Telegram, which includes the user's selection for the high boundary of the rating.
            """
            self.site.set_low(call.data)
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.set_state(call.from_user.id, MyStates.custom_high_set, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, "Set high: (you may have to wait up to 20 seconds)",
                                  reply_markup=self.gen_rating_choice())

        @self.bot.callback_query_handler(state=MyStates.custom_high_set,
                                         func=lambda call: call.data in self.oneTen)
        def cb_rating_handler_send_custom(call):
            """
            Completes the custom rating search by using the selected rating range.
            This method fetches the movie or series data based on the custom range set by the user and sends the results back to the user.
            It then resets the state and presents the main menu again.

            :param call: The callback query from Telegram, which includes the user's selection for the high boundary of the rating.
            """
            response_json = self.site.get_custom(call.data)
            choice = 'MOVIES' if self.site.params["type"] == 'movie' else 'SERIES'
            req = f"CUSTOM [{self.site.params.get('start_rating')}-{call.data}] {self.site.params['limit']} {choice}"

            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            self.bot.send_message(call.message.chat.id, text=req)
            titles = ''
            if "results" in response_json:
                for i, title in enumerate(response_json["results"]):
                    description = html.unescape(f"{i + 1}. {title['title']}\n\n"
                                                f"{title['synopsis']}\n\n"
                                                f"imdbrating: {title['imdbrating']}")
                    self.bot.send_photo(call.message.chat.id, photo=title["img"], caption=description)
                    titles += f"{title['title']}\n"
            else:
                self.bot.send_message(call.message.chat.id, text="no results")
            self.bot.delete_state(call.from_user.id, call.message.chat.id)
            self.bot.send_message(call.message.chat.id, text=self.INFO_TEXT, reply_markup=self.gen_inline_menu())
            self.log_user_action(call.from_user.id, req, titles)

        @self.bot.message_handler(func=lambda message: True)
        def handle_default(message):
            """
            Default handler for any messages not captured by other handlers.
            Deletes the user's message and sends a default error message.

            :param message: The message object from the user.
            :return: None
            """
            self.bot.delete_message(message.chat.id, message.message_id)

    def run(self):
        """
        Initiates the bot's polling to listen for Telegram updates continuously.
        This method is responsible for keeping the bot responsive to user commands and interactions.
        It includes the setup of custom filters to manage state and digit-based data accurately.
        """
        self.bot.add_custom_filter(custom_filters.StateFilter(self.bot))
        self.bot.add_custom_filter(custom_filters.IsDigitFilter())
        self.bot.infinity_polling(skip_pending=True)
