from datetime import timedelta
from RedisClient import Redis
from pyrogram import InlineQueryResultArticle, InputTextMessageContent
from errors import *
from time import sleep
import re
import subprocess
from typing import List

freemem_command = """free | awk 'FNR == 2 {print ($7/1048576)"GB / "($2/1048576)"GB" }'"""
loadavg_command = 'cat /proc/loadavg | cut -d" " -f1-3'
uptime_command = 'cat /proc/uptime | cut -d" " -f1'

empty_inline_query = [InlineQueryResultArticle(
    title="Please enter a query text", description="Type any word to search tags",
    input_message_content=InputTextMessageContent("Empty query string, I have nothing to do.")
)]

tags_gbl = 'tags:global'
desc_gbl = 'descriptions:global'
cmds_gbl = 'commands:global'
crdt_gbl = 'credits:global'

taggrps_gbl = 'taggroups:global'
taggrp_gbl = 'taggroup:global'
togrps_gbl = 'togroups:global'

cmd_format_template = '**Tag:** `{0}` By {1}\n**Description:** {2}\n**Snippet:**\n```{3}```'


def tagexists(tag: str) -> bool:
    return Redis.sismember(tags_gbl, tag)

def setcommand(tag : str, desc: str, command: str, credit: str) -> None:
    """
    To add or set a command into the database.
    Params:
    - `tag` : `str` , unique tag of the command
    - `desc` : `str` , description of the command
    - `command` : `str` , the command itself
    - `credit` : `str` , ident of the user who add the command

    Returns: `None`
    """
    Redis.sadd(tags_gbl, tag)
    Redis.hset(cmds_gbl, tag, command)
    Redis.hset(desc_gbl, tag, desc)
    Redis.hset(crdt_gbl, tag, credit)


def getcommand(tag: str) -> List[str]:
    """
    Get everything of the given tag, if exists.
    
    Returns: `list`
    - `[0]` : `str`, command snippet itself.
    - `[1]` : `str`, the description.
    - `[2]` : `str`, the credit.

    Raises: `TagNotFound` if the tag is not exist in the database.
    """
    if not Redis.sismember(tags_gbl, tag):
        raise TagNotFound(tag)
    desc = Redis.hget(desc_gbl, tag).decode('utf-8')
    command = Redis.hget(cmds_gbl, tag).decode('utf-8')
    credit = Redis.hget(crdt_gbl, tag).decode('utf-8')
    return (command, desc, credit)


def getcommand_f(tag: str) -> str:
    """
    Get a formatted string using getcommand().
    You could only use this if the tag EXISTS. Or the child call (`getcommand()`) will raise a exception.
    
    Params:

    - `tag` : `str` , the unique tag to get for.
    """
    cmd = getcommand(tag)
    command = cmd[0]
    desc = cmd[1]
    credit = cmd[2]
    user = get_user_name(credit)
    return cmd_format_template.format(tag, user, desc, command)


def tagsingroup(group):
    """
    Get all tags belongs to the group.  

    Returns:

    - `['', []]` if the group is not exist, there's a chance that the group was emptied.  
    - `list[str]` the list of the tags in the given group.  

    Raises: None
    """
    result = ['', []]
    res = Redis.smembers(f'taggroup:global:{group}')
    if res:
        result[0] = Redis.hget('g_description:global', group)
        for e in res:
            result[1].append(e.decode('utf-8'))            
    
    return result

def listtags(query, count=10):
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


def listgrps(query, count=20):
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


def get_user_name(ident):
    return Redis.hget('username', ident).decode('utf-8')

def put_user_name(ident, name):
    Redis.hset('username', ident, name)


def generatereply(query):
    """
    Generate the response to the inline query.

    Returns:
    
    - list[InlineQueryResultArticle]
    """
    anslist = []    # List of inlinequeryanswer
    if query.split(' ')[0] == 'group':  
        # Search for groups if the firstword of query is 'group'
        for i in listgrps(query.split(' ')[1]):
            tags = listtags(i)          
            # Acquire info of the group
            length = grouplength(i)
            text = "\n".join(tags)
            anslist.append(InlineQueryResultArticle(    
                # Add a result to anslist
                title=f'Tag Group {i}', 
                description=f'{length} Tags',
                input_message_content=InputTextMessageContent(
                    message_text=f'Tags:\n{text}'
                )
            ))
    else:
        q = query.split(' ')[0]     # Search for TAGS using keyword
        for i in listtags(q):       # Acquire tag info
            cmd = getcommand(i)
            command = cmd[0]
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


def delmsg(msg, timeout=15):
    """
    To delete a message, after 10 seconds.
    This will be helpful to the response of a command and the command message itself.
    """
    sleep(timeout)
    try:
        msg.delete()
    except:
        pass

