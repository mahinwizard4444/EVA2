import re
from os import environ

id_pattern = re.compile(r'^.\d+$')


def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

#
# # Bot information
# SESSION = environ.get('SESSION', 'Media_search')
# API_ID = int(environ['API_ID'])
# API_HASH = environ['API_HASH']
# BOT_TOKEN = environ['BOT_TOKEN']


# Bot information
SESSION = environ.get('SESSION', 'UFSBotz')
API_ID = int(environ.get('API_ID', '3607361'))
API_HASH = environ.get('API_HASH', 'c57bcc4b09591db4f90f60b469e8870f')
BOT_TOKEN = environ.get('BOT_TOKEN', '1635091229:AAE40V_s07MAKJRDM-LTL2dPIXyG9iW8rBk')

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', False))
PICS = (environ.get('PICS', 'https://telegra.ph/file/b62f9703cf805da50d5c4.jpg')).split()

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '631110062').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '0').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '631110062').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL', '0')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# https://github.com/Mahesh0253/pyrogram/archive/inline.zip
# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', 'mongodb+srv://jmjsoft:jins2010@ufsadvfilterbot.xckub.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
DATABASE_NAME = environ.get('DATABASE_NAME', 'Adv_Auto_Filter')
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Adv_Auto_Filter')

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-724048562'))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'TeamEvamaria')
P_TTI_SHOW_OFF = is_enabled((environ.get('P_TTI_SHOW_OFF', "False")), False)
IMDB = is_enabled((environ.get('IMDB', "False")), True)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "True")), False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", None)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", "{query} \n\n🏷 ᴛɪᴛʟᴇ: <a href={url}>{title}</a>\n🏷 ᴀʟsᴏ ᴋɴᴏᴡɴ ᴀs: {aka}\n🎭 ɢᴇɴᴇʀᴇs: {genres}\n📆 ʏᴇᴀʀ: <a href={url}/releaseinfo>{year}</a>\n🌟 ʀᴀᴛɪɴɢ: <a href={url}/ratings>{rating}</a> / 10")
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)
SHORT_LINK_API_KEY = environ.get("SHORT_LINK_API_KEY", None)
TG_MAX_MSG_SELECT = int(environ.get('TG_MAX_MSG_SELECT', 1000))
USE_AS_BOT = environ.get("USE_AS_BOT", True)
TMP_DOWNLOAD_DIRECTORY = "./UFSBotz/"
AUTO_DELETE = True
DELETE_TIME  = 120
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))

FILE_PROTECT = {}
IMPORTED = {}
HELPABLE = {}
dispatcher = None

LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two seperate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as diffrent buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your Correct IMDB template is {IMDB_TEMPLATE}"
