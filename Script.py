class script(object):
    START_TXT = """𝙷𝙴𝙻𝙾 {},
𝙼𝚈 𝙽𝙰𝙼𝙴 𝙸𝚂 <a href=https://t.me/{}>{}</a>, 𝙸 𝙲𝙰𝙽 𝙿𝚁𝙾𝚅𝙸𝙳𝙴 sᴇʀɪᴇs"""
    HELP_STRINGS = """
Hey Dear <b>{}</b>! My name is <b>𝕁𝕒𝕔𝕜𝕊𝕡𝕒𝕣𝕣𝕠𝕨</b>. I Am A Group 𝕄𝕠𝕧𝕚𝕖 Bot!
I Have Lots Of Handy Features, 

<b>Helpful commands</b>:
- /start: Starts me! You've probably already used this.
- /help: Sends this message; I'll tell you more about myself!
- You Can See How To Control Me In Here


All commands can be used with the following: /
"""
    HELP_TXT = """𝙷𝙴𝚈 {}
𝙷𝙴𝚁𝙴 𝙸𝚂 𝚃𝙷𝙴 𝙷𝙴𝙻𝙿 𝙵𝙾𝚁 𝙼𝚈 𝙲𝙾𝙼𝙼𝙰𝙽𝙳𝚂."""
    ABOUT_TXT = """✯ 𝙼𝚈 𝙽𝙰𝙼𝙴: {}
✯ 𝙲𝚁𝙴𝙰𝚃𝙾𝚁: <a href=https://t.me/TeamEvamaria>Team Eva Maria</a>
✯ 𝙻𝙸𝙱𝚁𝙰𝚁𝚈: 𝙿𝚈𝚁𝙾𝙶𝚁𝙰𝙼
✯ 𝙻𝙰𝙽𝙶𝚄𝙰𝙶𝙴: 𝙿𝚈𝚃𝙷𝙾𝙽 𝟹
✯ 𝙳𝙰𝚃𝙰 𝙱𝙰𝚂𝙴: 𝙼𝙾𝙽𝙶𝙾 𝙳𝙱
✯ 𝙱𝙾𝚃 𝚂𝙴𝚁𝚅𝙴𝚁: 𝙷𝙴𝚁𝙾𝙺𝚄
✯ 𝙱𝚄𝙸𝙻𝙳 𝚂𝚃𝙰𝚃𝚄𝚂: v1.0.1 [ 𝙱𝙴𝚃𝙰 ]"""
    SOURCE_TXT = """<b>NOTE:</b>
- Eva Maria is a open source project. 
- Our Malayalam subtitle bot - https://t.me/TvSeriesLand4U_Subtitle_Bot

<b>DEVS:</b>
- <a href=https://t.me/TeamEvamaria>Team Eva Maria</a>"""
    MANUELFILTER_TXT = """Help: <b>Filters</b>

- Filter is the feature were users can set automated replies for a particular keyword and UFS #V3.0 will respond whenever a keyword is found the message

<b>NOTE:</b>
1. 𝕁𝔸ℂ𝕂 𝕊ℙ𝔸ℝℝ𝕆𝕎 should have admin privilege.
2. only admins can add filters in a chat.
3. alert buttons have a limit of 64 characters.

<b>Commands and Usage:</b>
• /filter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>"""
    BUTTON_TXT = """Help: <b>Buttons</b>

- 𝕁𝔸ℂ𝕂 𝕊ℙ𝔸ℝℝ𝕆𝕎 Supports both url and alert inline buttons.

<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. Millie supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format

<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/TvSeriesLand4U)</code>

<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>

<b>NOTE:</b>
1. Make me the admin of your channel if it's private.
2. make sure that your channel does not contains camrips, porn and fake files.
3. Forward the last message to me with quotes.
 I'll add all the files in that channel to my db."""
    CONNECTION_TXT = """Help: <b>Connections</b>

- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM

<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
these are the extra features of Eva Maria

<b>Commands and Usage:</b>
• /id - <code>get id of a specified user.</code>
• /info  - <code>get information about a user.</code>
• /imdb  - <code>get the film information from IMDb source.</code>
• /search  - <code>get the film information from various sources.</code>"""
    ADMIN_TXT = """Help: **Admin mods**

**NOTE:**
This module only works for my admins

**Commands and Usage:**
• /logs - `to get the recent errors`
• /stats - `to get status of files in db.`
• /delete - `to delete a specific file from db.`
• /users - `to get list of my users and ids.`
• /chats - `to get list of the my chats and ids `
• /leave  - `to leave from a chat.`
• /disable  -  `do disable a chat.`
• /ban  - `to ban a user.`
• /unban  - `to unban a user.`
• /channel - `to get list of total connected channels`
• /broadcast - `to broadcast a message to all users`"""
    STATUS_TXT = """<b>★ Tᴏᴛᴀʟ Fɪʟᴇs:</b> <code>{}</code>
<b>★ Tᴏᴛᴀʟ Usᴇʀs:</b> <code>{}</code>
<b>★ Tᴏᴛᴀʟ Cʜᴀᴛs:</b> <code>{}</code>
<b>★ Usᴇᴅ Sᴛᴏʀᴀɢᴇ:</b> <code>{}</code>
<b>★ Fʀᴇᴇ Sᴛᴏʀᴀɢᴇ:</b> <code>{}</code>"""
    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""
