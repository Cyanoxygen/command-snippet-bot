from utils import *
from bot import bot
from redisclient import Redis
from pyrogram import Client, Filters
from config import bot_name

@bot.on_message(Filters.private & Filters.command('accept'))
def handler_acceptrep(cli, msg):
	if isauthed(str(msg.from_user.id)):
		if len(msg.command) == 2:
			tag = msg.command[1]
			chat = Redis.hget('reportedfrom:global', tag).decode('utf-8')
			user = str(msg.from_user.id)
			bot.send_message(
				chat_id=chat,
				text=ntf_accepted.format(get_user_name(user), tag)
			)
			rmreport(tag)
	else:
		msg.reply('Insufficiant permission')


@bot.on_message(Filters.private & Filters.command('reject'))
def handler_acceptrep(cli, msg):
	if isauthed(str(msg.from_user.id)):
		if len(msg.command) == 2:
			tag = msg.command[1]
			chat = Redis.hget('reportedfrom:global', tag).decode('utf-8')
			user = str(msg.from_user.id)
			bot.send_message(
				chat_id=chat,
				text=ntf_rejected.format(get_user_name(user), tag)
			)
	else:
		msg.reply('Insufficiant permission')
	delmsg(msg, 0)


@bot.on_message(Filters.command(['addadmin', f'addadmin@{bot_name}']))
def handler_addadmin(cli, msg):
	if str(msg.from_user.id) == bot_master:
		if len(msg.command) > 1:
			users = []
			for user in msg.command[1:]:
				Redis.sadd(f'botadmin:{bot_name}', user)
			
			delmsg(msg.reply(f'Done! These users are now privileged:\n{users}'))
	
	else:
		delmsg(msg.reply('Insufficient permission'))

	delmsg(msg, 0)


@bot.on_message(Filters.command(['rmadmin', f'rmadmin@{bot_name}']))
def handler_addadmin(cli, msg):
	if str(msg.from_user.id) == bot_master:
		if len(msg.command) > 1:
			users = []
			for user in msg.command[1:]:
				Redis.srem(f'botadmin:{bot_name}', user)
			
			delmsg(msg.reply(f'Done! These users are now removed from privileged list:\n{users}'))
	
	else:
		delmsg(msg.reply('Insufficient permission'))

	delmsg(msg, 0)


@bot.on_message(Filters.command(['listadmins', f'listadmins@{bot_name}']))
def handler_listadmins(cli, msg):
	if isauthed(str(msg.from_user.id)):
		admins = []
		for i in Redis.smembers(f'botadmin:{bot_name}'):
			admins.append(i.decode('utf-8'))
		delmsg(msg.reply(f'List of bot admins:\n{admins}'), 30)

	else:
		delmsg(msg.reply('Insufficient permission'))
	delmsg(msg, 0)

