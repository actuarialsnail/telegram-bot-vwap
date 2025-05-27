import logging

logger = logging.getLogger("bot_logger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('hashkey_telegram_bot.log')
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)