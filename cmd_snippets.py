from bot import bot, sendmaster
from utils import *
from pyrogram import Client, Filters, Message, InlineQuery
from redisclient import Redis
from config import *
from errors import *
from texts import *
import subprocess

@bot.on_message(Filters.group & Filters.command(['addsnippet', f'addsnippet@{bot_name}']))
def handler_addsnippet(cli: Client, msg: Message) -> None:
	if len(msg.command) > 2:
		lines = msg.text.split('\n')
		if len(lines) >= 3:
			try:
				tag = msg.command[1]
				desc = lines[1]
				commands = '\n'.join(lines[2:])
				credit = str(msg.from_user.id)
				setsnippet(tag, desc, commands, credit)
				Redis.hset('username', credit, msg.from_user.first_name)
				delmsg(msg.reply(f'Done, the snippet was successfully added:\n{getsnippet_f(tag)}'), 30)
				sendmaster(f'New Tag:\n{getsnippet_f(tag)}')
			except Exception as e:
				delmsg(msg.reply(e))
				return
		else:
			delmsg(msg.reply(help_text_addsnipppet))
	else:
		delmsg(msg.reply(help_text_addsnipppet))
	delmsg(msg, 0)


@bot.on_message(Filters.group & Filters.command(['editsnippet', f'editsnippet@{bot_name}']))
def handler_editsnippet(cli, msg):
	if len(msg.command) > 1:
		lines = msg.text.split('\n')
		if len(lines) >= 2:
			try:
				tag = msg.command[1]
				edit = msg.command[2]
				content = '\n'.join(lines[1:])
				editsnippet(tag, edit, content)
			except Exception as e:
				delmsg(msg.reply(e))
				return
			
			delmsg(msg.reply(f'Done, the snippet was edited:\n{getsnippet_f(tag)}'))
		else:
			delmsg(msg.reply(help_text_editsnippet))
	else:
		delmsg(msg.reply(help_text_editsnippet))
	delmsg(msg, 0)


@bot.on_message(Filters.group & Filters.command(['delsnippet', f'delsnippet@{bot_name}']))
def handler_delsnippet(cli, msg):
	if len(msg.command) > 1:
		try:
			user = str(msg.from_user.id)
			tag = msg.command[1]
			_text = getsnippet_f(tag)
			pop = ntf_deleted.format(_text)
			rmsnippet(tag, user)
		except Exception as e:
			delmsg(msg.reply(e))
			return
		delmsg(msg.reply(pop))
	delmsg(msg)


@bot.on_inline_query()
def handler_query(client: Client, iquery: InlineQuery):
	lst = iquery.query.split(' ')
	if lst[0] == '':
		bot.answer_inline_query(
			inline_query_id=iquery.id,
			results=empty_inline_query
		)
		return
	bot.answer_inline_query(
		inline_query_id=iquery.id,
		results=generatereply(lst[0])
	)


@bot.on_message(Filters.command(['reportsnippet', f'reportsnippet@{bot_name}']))
def handler_reportsnippet(cli, msg):
	if len(msg.command) > 2:
		lines = msg.text.split('\n')
		if len(lines) > 1:
			try:
				tag = msg.command[1]
				reason = '\n'.join(lines[1:])
				user = str(msg.from_user.id)
				chat = str(msg.chat.id)
				addreport(
					tag=tag,
					reason=reason,
					user=user,
					chat=chat
					)
				Redis.hset('username', user, msg.from_user.first_name)
				sendmaster(f'New Report: \nTag: {getsnippet_f(tag)}\nReported by {get_user_name(user)}\nReason: {reason}')
				delmsg(msg.reply(ntf_ticket_sent))
			except Exception as e:
				delmsg(msg.reply(e))
				return
		else:
			delmsg(msg.reply(help_text_report))
	else:
		delmsg(msg.reply(help_text_report))
	delmsg(msg, 0)


# Miscellaneous utilities
@bot.on_message(Filters.command(['ping', f'ping@{bot_name}']))
def handler_ping(cli, msg):
	try:
		uptime = subprocess.getoutput(uptime_command)
		loadavg = subprocess.getoutput(loadavg_command)
		freemem = subprocess.getoutput(freemem_command)
		uptime = str(timedelta(seconds=int(float(uptime))))
		delmsg(msg.reply(
			f'I\'m alive.\nYour ID:`{msg.from_user.id}`\nChat ID:{msg.chat.id}\nUptime: `{uptime}`\nLoadavg: `{loadavg}`\nFree: `{freemem}`'),
		30)
	except:
		delmsg(msg.reply(f'I\'m alive!\nYour ID:`{msg.from_user.id}`\nChat ID:{msg.chat.id}'))
	delmsg(msg, 0)

