from config import bot_name
import logging

logging.basicConfig(level=25, format = '%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s')   # to prevent pyrogram from spamming logs
logger = logging.getLogger(bot_name)
