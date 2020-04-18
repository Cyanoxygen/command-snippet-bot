from pyrogram import Client, Filters
from RedisClient import Redis
from config import *
from utils import *
from texts import *

bot = Client(
    session_name=bot_name,
    bot_token=bot_token
)


@bot.on_message(Filters.command(['addsnippet', f'addsnippet@{bot_name}']))
def handler_addsnippet(cli, msg):
    if len(msg.command) > 2:
        lines = msg.text.split('\n')
        if len(lines) >= 3:
            tag = msg.command[1]
            if tagexists(tag):
                delmsg(msg.reply(f'Tag already exists.\n{getcommand_f(tag)}'))
                delmsg(msg, 0)
                return
            desc = lines[1]
            commands = '\n'.join(lines[2:])
            credit = str(msg.from_user.id)
            setcommand(tag, desc, commands, credit)
            Redis.hset('username', credit, msg.from_user.first_name)
            delmsg(msg.reply(f'Done, the snippet was successfully added:\n{getcommand_f(tag)}'), 30)
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
            tag = msg.command[1]
            if not tagexists(tag):
                delmsg(msg.reply(err_tag_not_exist))
                delmsg(msg, 0)
                return
            if str(msg.from_user.id) != getcommand(tag)[2]:
                delmsg(msg.reply(err_not_your_tag))
                delmsg(msg, 0)
                return
            edit = msg.command[2]
            content = '\n'.join(lines[1:])
            if edit in ['desc', 'snippet']:
                editsnippet(tag, edit, content)

            delmsg(msg.reply(f'Done, the snippet was edited:\n{getcommand_f(tag)}'))
        else:
            delmsg(msg.reply(help_text_editsnippet))
    else:
        delmsg(msg.reply(help_text_editsnippet))
    delmsg(msg, 0)
            

@bot.on_inline_query()
def handler_query(client, iquery):
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
    delmsg(msg.reply(f'I\'m alive.\nYour ID:`{msg.from_user.id}`\nChat ID:{msg.chat.id}\nUptime: `{uptime}`\nLoadavg: `{loadavg}`\nFree: `{freemem}`'), 30)
    delmsg(msg, 0)


bot.start()
