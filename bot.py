#!/usr/bin/env python3
# This is the TGbot part of this bot.
# This file only defines a pyrogram Bot client, and a simple function which sends a text to bot_master.


from pyrogram import Client
from config import bot_name, bot_token, bot_master
from logger import logger


bot = Client(
	session_name=bot_name,
	bot_token=bot_token
)

def sendmaster(text: str) -> None:
	bot.send_message(
		chat_id=bot_master,
		text=text
		)

if __name__ == "__main__":
    logger.fatal('Please run ./run.py instead.\n')
    exit(1)
