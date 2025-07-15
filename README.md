# Movie Series Finder Bot

The Movie Series Finder Bot is a Telegram bot designed to help users discover the best movies and series based on their preferences. It offers different commands to retrieve high-rated content, low-rated content, and allows for custom searches based on specific rating ranges.

## Features

- Search for top-rated movies and series.
- Search for low-rated movies and series.
- Custom search by specifying a rating range.
- View the history of the last 5 requests made.

## Installation

To run this bot, you need Python 3.7+ and some packages from the Python package index. Follow these steps to set up:

1. **Clone the repository:**
   ```bash
   git clone https://gitlab.skillbox.ru/nurlan.nurlybay/python_basic_diploma.git
   cd python_basic_diploma

2. **Install dependencies:**
   ```bash
   python3 -m venv .venv
   pip install -r requirements.txt
   
3. **Install dependencies:**
   ```
   Create a .env file in the root directory of your project and include the following variables:
   SITE_API=<your_site_api_key>
   HOST_API=<your_host_api>
   BOT_TOKEN=<your_telegram_bot_token>
   
4. **Run the bot:**
   ```bash
   python main.py

## Usage

After you start the bot, you can interact with it using the following commands:
- /start - Display the welcome message and command menu.

## Inline Commands

- low - Fetch a list of low-rated movies or series.
- high - Fetch a list of high-rated movies or series.
- custom - Perform a custom search by setting a specific rating range.
- history - Display the last 5 requests made by the user.
- menu - Open the main menu InlineKeyboard with the 4 commands listed above.
- Movies/Series: Choose between movies or series to focus your search.
- Number Selection: After choosing movies or series, select how many results you want to retrieve.
- Rating Selection: For custom searches, set the minimum and maximum ratings.

## Development
This bot uses the Python Telegram Bot API and connects to a third-party API for fetching movie data. It employs SQLite to store user requests and manage history.

## Contributions
Contributions are welcome! Please fork the repository and submit a pull request with your features or fixes.

## License
The project is unlicensed.
