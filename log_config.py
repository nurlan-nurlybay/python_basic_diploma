import logging

logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('app.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)
