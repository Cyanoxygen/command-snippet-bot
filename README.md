# Command Snippet Bot

<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="86" height="20"><linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r"><rect width="86" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#r)"><rect width="49" height="20" fill="#555"/><rect x="49" width="37" height="20" fill="#26c6da"/><rect width="86" height="20" fill="url(#s)"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"><text x="255" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="390">Python</text><text x="255" y="140" transform="scale(.1)" textLength="390">Python</text><text x="665" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="270">3.7+</text><text x="665" y="140" transform="scale(.1)" textLength="270">3.7+</text></g></svg> <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="118" height="20"><linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r"><rect width="118" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#r)"><rect width="63" height="20" fill="#555"/><rect x="63" width="55" height="20" fill="#26c6da"/><rect width="118" height="20" fill="url(#s)"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"><text x="325" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">pyrogram</text><text x="325" y="140" transform="scale(.1)" textLength="530">pyrogram</text><text x="895" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="450">0.16.0+</text><text x="895" y="140" transform="scale(.1)" textLength="450">0.16.0+</text></g></svg>

> I will try to remember every command you told me.

A bot stores command sinppets identified by their unique tags.

Original idea by Chisaka.

## Run

### Requirements

- Python 3.7+
- Modules (can be installed via `pip`):

  - `pyrogram` : to run the bot itself.
  - `redis` : the backend database

- A running Redis server in localhost or remote
  
Clone or download this repo using any means you can use:

```
git clone https://github.com/Cyanoxygen/command-snippet-bot
```

Then edit `config.ini` and fill your App ID and App Hash.

Last, edit `config.py` and fill your bot username (exclude `@` , e.g. `CmdSnipBot` ), bot token, your User ID (yes, your unique integer UID), and Redis server, port, password (if you have). 

And just simply run `run.py` by any means you can execute it:

```
./run.py
# Or
python3 ./run.py    # or etc
```

## Note

- The command snippet you submit will be available to public. There's no user-specific settings.

## Usage

- To search a tag, you can use inline mode:
  
  ```@bot_name keyword```

- To add a snippet, please use command `/addsnippet` :
  
  ```
  /addsnippet tag
  description
  snippets...
  ```

  _You can insert multi-line snippets into snippets section._

- To edit a snippet added by YOURSELF:
  ```
  /editsnippet tag desc|snippet
  <new text or snippet here>
  ```

  - Note that you can only modify snippets which created by YOURSELF, modification to snippets created by other user is not accepted.

- To remove your snippet from our database:
  ```
  /delsnippet tag
  ```

  Then bot will "pop" the snippet to be deleted for you, then delete it immidiately.
  Since there's no confirmation please consider twice before you delete a snippet, and you can add it back at any time :)

- If you see a snippet which contains words conflicting with common sense, feel free to use this command to send a report to us:
  ```
  /reportsnippet tag
  reason
  ```

## Insights

### Code of conduct

We divide the bot into several parts, and each part is represented in a single Python file:

- `bot.py`
  Defines a bot object using `pyrogram.Client`. Every action involved the bot should import `bot` first.

- `config.ini`
  Pyrogram `config.ini` file, contains App ID and App Hash.

- `config.py`
  bot config file, contains some necessary parameters in order to run this bot.

- `cmd_snippet.py`
  This file imports `bot` class, defines some handlers about bot commands, which modifies the Snippet database.
  You can see lots of command handlers in this file, and these commands is just used for snippet related things. Plus, there's a inline query handler, to search tags by using inline uqery.

- `cmd_moderator.py`
  This file imports `bot` class, defines some handlers about managing this bot.
  Commands defined in this file will be only available for bot master and bot administrators.

- `errors.py`
  Defines some exceptions raised by backend.

- `texts.py`
  Defines some text massages used widely in these code.

- `utils.py`
  The actual backend of the bot, responsible for interacting with database, managing bot moderators and etc.

- `run.py`
  To run this bot, just execute this file.

### Database structure

This bot uses Redis as the backend database.

For every command snippets you should give them a unique tag (or ID). Then the tag and corresponding command snippet, description, and credit (the user identifier that added this snippet) will be stored as follows:

| Key                   | Type   | Description                                                  |
| --------------------- | ------ | ------------------------------------------------------------ |
| `tags:global`         | `set`  | To store all of the tags.                                    |
| `commands:global`     | `hash` | To store all commands corresponding to each tag.             |
| `descriptions:global` | `hash` | To store the given description of each tag.                  |
| `credits:global`      | `hash` | To store the ident of user who added the command to the bot. |
| `createdby:{credit}`  | `set`  | To store the tags created by this user                       |

Plus, for more friendly outputs, we need a extra hash to match the username and user ident, so that the user ID won't be showed in the result message:

```redis
HSET usernames:global userid first_name
```

To get the username, you can simply call `get_user_name(ident: str)` .

For groups, the idea is that a tag may belong to more than one group, a group could contain many of tags. This is usually more complicated than tags.  
To handle groups completely, we need at least 3 keys per tag: 

| Key                       | Type   | Description                                       |
| ------------------------- | ------ | ------------------------------------------------- |
| `taggroups:global`        | `set`  | To store all of the group names.                  |
| `g_description:global`   | `hash` | To store description of the group.                |
| `taggroup:global:{group}` | `set`  | To store all of the tags belong to this `group` . |
| `togroups:global:{tag}`   | `set`  | To store all of the groups belong to the `tag`.   |

Due to the flaw of my design, this bot code should be strictly written. It means that to modify a snippet you should look for all of these keys to find something related to this tag.

Note: these tags should be global. Multiuser could not be handled because I am poor in programming.

### Inline Query Procedures

The code shows you the procedures in answering inline queries:

First, the bot fetches the query text user entered. Only one word(Including almost symbols) is accepted.

```python
@bot.on_inline_query()
def handler_query(client, iquery):
    lst = iquery.query.split(' ')  
    if lst[0] == '':
```

When bot received a inline query, it will look for the first word user inputed.    
Even emptty string (including spaces) is breakable, the first element returned by `split()` is always empty.  
If there's no input, bot will reply a notice which tells that the user must provide a keyword.  
If there's input, bot will pick up the first word to search in the database:

```python
generatereply(lst[0])
# defination of generatereply(query):
q = query.split(' ')[0]     # Search for TAGS using keyword
for i in listtags(q):       # Acquire tag info
  # Add information to the result list and return to answer_inline_query()
```
Please read code for more info.

