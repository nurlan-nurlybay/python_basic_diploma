"""
For some reason I had trouble using logging.basicConfig(), if it works for you, you do not need this file.
However, all the loggers in the project use this logger, so you will need to refactor all every
logger.info() to logging.info (just keep using this logeer)
"""

import logging

logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('app.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)
