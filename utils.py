import re
import subprocess
import traceback

from config import bot_name, bot_master
from datetime import timedelta
from time import sleep
from typing import List, NewType

from pyrogram import InlineQueryResultArticle, InputTextMessageContent, Message

from errors import *
from redisclient import Redis
from texts import *

freemem_command = """free | awk 'FNR == 2 {print ($7/1048576)"GB / "($2/1048576)"GB" }'"""
loadavg_command = 'cat /proc/loadavg | cut -d" " -f1-3'
uptime_command = 'cat /proc/uptime | cut -d" " -f1'

Tags = List[str]
Snippet = List[str]
Formated = str

empty_inline_query = [InlineQueryResultArticle(
	title="Please enter a query text", description="Type any word to search tags",
	input_message_content=InputTextMessageContent("Empty query string, I have nothing to do.")
)]

TAGS_GBL = 'tags:global'
DESC_GBL = 'descriptions:global'
CMDS_GBL = 'commands:global'
CRDT_GBL = 'credits:global'
CREATEDBY = 'createdby:{}'

TAGGRPS_GBL = 'taggroups:global'
TAGGRP_GBL = 'taggroup:global'
TOGRPS_GBL = 'togroups:global'


def tagexists(tag: str) -> bool:
	return Redis.sismember(TAGS_GBL, tag)


def isauthed(user: str, tag: str='', adminonly: bool = False) -> bool:
	'''
	Determines if the user is able to do something, e.g. to edit a snippet or to delete a snippet.  
	Only the user who created the snippet, bot admins and bot master (see config.py) can do such an operation.

	Params:
	
	- `tag` : the tag needed to be authenticated.
	- `user` : the user who takes the action.
	- `adminonly` : `bool` , if the action is admin only, then set this to True.

	Return:  
	`True` if the user is qualified or
	`False` if the user is not qualified.
	'''
	qualified = [bot_master]
	# Get bot admins
	_ = Redis.smembers(f'botadmin:{bot_name}')
	for a in _:
		qualified.append(a.decode('utf-8'))
	
	# Get the credit of the tag
	if tag:
		credit = getsnippet(tag)[2]
		qualified.append(credit)
	
	return user in qualified


def setsnippet(tag: str, desc: str, command: str, credit: str) -> None:
	"""
	To add or set a command into the database.
	Params:
	- `tag` : `str` , unique tag of the command
	- `desc` : `str` , description of the command
	- `command` : `str` , the command itself
	- `credit` : `str` , ident of the user who add the command

	Returns: `None`
	"""
	if tagexists(tag):
		raise TagAlreadyExists

	Redis.sadd(TAGS_GBL, tag)
	Redis.hset(CMDS_GBL, tag, command)
	Redis.hset(DESC_GBL, tag, desc)
	Redis.hset(CRDT_GBL, tag, credit)
	Redis.sadd(CREATEDBY.format(credit), tag)


def rmsnippet(tag: str, user: str) -> None:
	"""
	To remove a command into the database.
	Params:
	- `tag` : `str` , unique tag of the command to be removed
	- `user` : `str` , the user who takes the action, for verification use.

	Returns: `None`
	Raises:
	
	- `TagNotFound` if tag is not found.
	- `TagNotOwned` if tag is not owned by the user.
	"""
	if not tagexists(tag):
		raise TagNotFound
	
	if not isauthed(user, tag):
		raise TagNotOwned

	credit = Redis.hget(CRDT_GBL, tag).decode('utf-8')
	Redis.srem(TAGS_GBL, tag)
	Redis.hdel(CMDS_GBL, tag)
	Redis.hdel(DESC_GBL, tag)
	Redis.srem(CREATEDBY.format(credit), tag)
	Redis.hdel(CRDT_GBL, tag)


def editsnippet(tag: str, edit: str, content: str, user: str) -> None:
	'''
	Edit a snippet. Which to edit depends on the selection.
	
	Params:

	- `tag` : `str` , the tag to edit.
	- `edit` : `str` - `desc` or `snippet` , to choose what to edit.
	- `content` : `str` , the content to be replaced.
	- `user` : `str` , the user who takes action.
	'''
	if not tagexists:
		raise TagNotFound
	if not isauthed(user, tag=tag):
		raise TagNotOwned

	if edit == 'desc':
		Redis.hset(DESC_GBL, tag, content)
	elif edit == 'snippet':
		Redis.hset(CMDS_GBL, tag, content)
	else:
		raise Exception(err_invalid_edit)


def getsnippet(tag: str) -> Snippet:
	"""
	Get everything of the given tag, if exists.

	Returns: `list`
	- `[0]` : `str`, command snippet itself.
	- `[1]` : `str`, the description.
	- `[2]` : `str`, the credit.

	Raises: `TagNotFound` if the tag is not exist in the database.
	"""
	if not Redis.sismember(TAGS_GBL, tag):
		raise TagNotFound
	desc = Redis.hget(DESC_GBL, tag).decode('utf-8')
	command = Redis.hget(CMDS_GBL, tag).decode('utf-8')
	credit = Redis.hget(CRDT_GBL, tag).decode('utf-8')
	return (command, desc, credit)


def getsnippet_f(tag: str) -> Formated:
	"""
	Get a formatted string using getcommand().
	You could only use this if the tag EXISTS. Or the child call (`getcommand()`) will raise a exception.

	Params:

	- `tag` : `str` , the unique tag to get for.
	"""
	if not tagexists(tag):
		raise TagNotFound

	cmd = getsnippet(tag)
	command = cmd[0]
	desc = cmd[1]
	credit = cmd[2]
	user = get_user_name(credit)
	return cmd_format_template.format(tag, user, desc, command)


def tagsingroup(group: str) -> List[Tags]:
	"""
	Get all tags belongs to the group.

	Returns:

	- `['', []]` if the group is not exist, there's a chance that the group was emptied.
	- `[str, list[str]]` the first string is the description of the group, the latter is a list of the tags in the given group.

	Raises: None
	"""
	result = ['', []]
	res = Redis.smembers(f'taggroup:global:{group}')
	if res:
		result[0] = Redis.hget('g_description:global', group)
		for e in res:
			result[1].append(e.decode('utf-8'))

	return result


def listtags(query: str, count: int = 10) -> List[str]:
	"""
	List all tags matches the pattern.

	Returns:

	- `[]` if no tags was found
	- `list[str]` the list of the tags matched the query pattern

	Raises: None
	"""
	result = []
	res = Redis.sscan('tags:global', match=f'*{query}*')[1]
	if res:
		for e in res:
			result.append(e.decode('utf-8'))

	return result


def grouplength(group):
	return Redis.scard(f'taggroups:global:{group}')


def iscreatedby(credit: str, tag: str) -> bool:
	"""
	Determines if the `tag` is created by user `credit`.
	Just simply calling Redis method.

	Return `True` or `False` .
	"""
	return Redis.hexists(CREATEDBY.format(credit), tag)


def listgrps(query: str, count: int = 20) -> List[str]:
	"""
	List all tags matches the pattern.
	Params:

	- `query`: `str` , query string
	- `count`: `str` , counts of the given results.

	Returns:

	- `[]` if no tags was found
	- `list[str]` the list of the groups matched the query pattern

	Raises: None
	"""
	result = []
	res = Redis.sscan('taggroups:global', match=f'*{query}*', count=count)[1]
	if res[1]:
		for e in res[1]:
			result.append(e.decode('utf-8'))

	return res


def addreport(tag: str, reason: str, user: str, chat:str) -> None:
	"""
	Record a abuse report.
	Will be removed after being processed.
	"""
	if not tagexists(tag):
		raise TagNotFound
	
	Redis.sadd('reported:global', tag)
	Redis.hset('repreason:global', tag, reason)
	Redis.hset('reportedby:global', tag, user)
	Redis.hset('reportedfrom:global', tag, chat)


def rmreport(tag):
	"""
	Remove a recorded report.
	This is not related to tag itself, whether the snippet was deleted or not.
	"""
	Redis.srem('reported:global', tag)
	Redis.hdel('repreason:global', tag)
	Redis.hdel('reportedby:global', tag)
	Redis.hdel('reportedfrom:global', tag)


def get_user_name(ident: str) -> str:
	return Redis.hget('username', ident).decode('utf-8')


def put_user_name(ident: str, name: str) -> str:
	Redis.hset('username', ident, name)


def replace_keyword(src: str, rpls: list) -> str:
	"""
	Replace keyword ::r:: in `src` with provided text in rpls.
	"""
	replace_count = src.count("::r::")
	if replace_count == 0:
		return src
	length = len(rpls)
	replaced = "".join(src) # Make a copy
	for text in rpls:
		replaced = replaced.replace("::r::", text, 1)

	return replaced


def generatereply(query: list) -> List[InlineQueryResultArticle]:
	"""
	Generate the response to the inline query.

	Returns:

	- list[InlineQueryResultArticle]
	"""
	anslist = []  # List of inlinequeryanswer
	if query[0] == 'group':
		# Search for groups if the firstword of query is 'group'
		for i in listgrps(query[1]):
			_ = tagsingroup(i)
			tags = _[1]
			desc = _[0]
			# Acquire info of the group
			length = grouplength(i)
			text = "\n".join(tags)
			anslist.append(InlineQueryResultArticle(
				# Add a result to anslist
				title=f'Tag Group {i} {length} tags',
				description=desc,
				input_message_content=InputTextMessageContent(
					message_text=f'Tags:\n{text}'
				)
			))
	else:
		pattern =query[0]
		argv = query[1:] if len(query) > 0 else [] 
		for i in listtags(pattern):  # Acquire tag info
			cmd = getsnippet(i)
			command = replace_keyword(cmd[0], argv)
			desc = cmd[1]
			credit = cmd[2]
			anslist.append(InlineQueryResultArticle(
				title=i,
				description=desc,
				input_message_content=InputTextMessageContent(
					message_text=cmd_format_template.format(i, get_user_name(credit), desc, command)
				)
			))
	if len(anslist) == 0:
		anslist.append(InlineQueryResultArticle(
			title=f'No result of {query}',
			input_message_content=InputTextMessageContent(f'No results found: {query}')
		))
	return anslist


def delmsg(msg: Message, timeout: int = 15) -> None:
	"""
	This function is an alias for sleep_timeout_and_delmsg()
	"""
	sleep_timeout_and_delmsg(msg, timeout)


def sleep_timeout_and_delmsg(msg: Message, timeout: int = 15) -> None:
	"""
	To delete a message after a timeout.
	The timeout is 15 by default.
	This will be helpful to the response of a command and the command message itself.
	"""
	sleep(timeout)
	try:
		msg.delete()
	except:
		pass

