from pyrogram import Client, Filters, Message, InlineQuery
from RedisClient import Redis
from config import *
from errors import *
from utils import *
from texts import *


bot = Client(
	session_name=bot_name,
	bot_token=bot_token
)


@bot.on_message(Filters.command(['addsnippet', f'addsnippet@{bot_name}']))
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
			except Exception as e:
				delmsg(msg.reply(e))
				return
			Redis.hset('username', credit, msg.from_user.first_name)
			delmsg(msg.reply(f'Done, the snippet was successfully added:\n{getsnippet_f(tag)}'), 30)
		else:
			delmsg(msg.reply(help_text_addsnipppet))
	else:
		delmsg(msg.reply(help_text_addsnipppet))
	delmsg(msg, 0)


@bot.on_message(Filters.command(['editsnippet', f'editsnippet@{bot_name}']))
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


@bot.on_message(Filters.command(['delsnippet', f'delsnippet@{bot_name}']))
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


# Miscellaneous utilities
@bot.on_message(Filters.command(['ping', f'ping@{bot_name}']))
def handler_ping(cli, msg):
	uptime = subprocess.getoutput(uptime_command)
	loadavg = subprocess.getoutput(loadavg_command)
	freemem = subprocess.getoutput(freemem_command)
	uptime = str(timedelta(seconds=int(float(uptime))))
	delmsg(msg.reply(
		f'I\'m alive.\nYour ID:`{msg.from_user.id}`\nChat ID:{msg.chat.id}\nUptime: `{uptime}`\nLoadavg: `{loadavg}`\nFree: `{freemem}`'),
	       30)
	delmsg(msg, 0)


bot.start()
