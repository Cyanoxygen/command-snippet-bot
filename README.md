# Command Snippet Bot

> I will try to remember every command you told me.

A bot stores command sinppets identified by their unique tags.

Original idea by Chisaka.

## Run

### Requirements

- Modules (can be installed via `pip`):

  - `pyrogram` : to run the bot itself.
  - `redis` : the backend database

- A running Redis server in localhost or remote

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

## Insights

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

