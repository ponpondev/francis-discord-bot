# logger setup
import logging
import sys


def setup_logger(logger, filename='bot.log', console=True):
    if logger.handlers:
        return

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s: %(message)s (%(filename)s:%(lineno)d)')

    fileHandler = logging.FileHandler(filename=filename, encoding='utf-8')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
