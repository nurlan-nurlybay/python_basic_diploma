from config import AppSettings
from database.common.models import History
from database.core import db_manage
from log_config import logger
from tg_API.core import Bot
from site_API.core import SiteApi


def main():
    app = AppSettings()
    site = SiteApi(app.site_api.get_secret_value(), app.host_api)
    bot = Bot(app.bot_token.get_secret_value(), site)
    bot.setup_handlers()
    # db_manage.clear_all(History)
    bot.run()


if __name__ == '__main__':
    logger.info('Application started.')
    main()
    logger.info('Application finished.')
