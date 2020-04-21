help_text_inline = '''Use inline mode to search tags.'''

cmd_format_template = '**Tag:** `{0}` By {1}\n**Description:** {2}\n**Snippet:**\n```{3}```'

err_tag_not_exist = 'Tag does not exist! Exiting.'
err_not_your_tag = 'You do not own this snippet, or you do not have permission to modify. To edit or remove this snippet, please contact the creator of the snippet.'
err_tag_exists = 'Sorry but the tag is already exists. Choose a different name and try again :)'
err_invalid_edit = 'Invalid edit keyword, the second param must be `desc` for replacing descriptions or `snippet` for replacing the snippet itself.'

ntf_deleted = 'Done! This snippet was deleted, let me "pop" this snippet for you: \n{}'
ntf_ticket_sent = 'DOne! Your ticket was sent to Bot Admins. Please wait patiently until we do something.'

help_text_about = '''This bot can help you to store command or code snippets, identified by a Tag.
Please note that your snippet will be publicly available.

You can use inline mode to search tags!

Moreinfo at https://github.com/Cyanoxygen/command-snippet-bot
'''

help_text_addsnipppet = '''Add a snippet to this bot.
Usage: ```/addsnippet tag
Description
commands```
Note: there is a line break between these elements. You can insert multi-line commands here.

Example:
```/addsnippet youtube-dl-ins
Install youtube-dl
sudo wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl
sudo chmod a+rx /usr/local/bin/youtube-dl```
'''

notify_accepted = '''{0}, Your abuse report of {1} was accepted and we removed it from the database.
Thank you! Your effort will be appreciated. 
'''

notify_rejected = '''Sorry {0}, but your abuse report of {1} was denied. 
Thank you for the effort!
'''

help_text_editsnippet = '''Edit a snippet created by yourself.
Usage: ```/editsnippet tag desc|snippet
New content to edit
```
Example: if you have a typo in your snippet, you can replace it by:
```/editsnippet tag snippet
new_command_here
``` 
'''

help_text_delsnippet = '''Remove a snippet created by yourself.
Usage: `/delsnippet tag`

Nothing to tell you here :) There's no confirmation, your snippet will be deleted immidiately. 
'''

help_text_report = '''Report abuse!
See a snippet inappropriate for most of us? Then report it! Simply send a request using this command and we will delete it for you all.

Usage:
```/reportsnippet tag
Your reason for the request
```
'''
