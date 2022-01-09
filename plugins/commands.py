import json
import os
import sys
import time
import logging
import random
import asyncio

from bot import Bot
from Script import script
from pyrogram import Client, filters
from database.batch_db import get_batch
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, LOG_CHANNEL, PICS, HELPABLE
from plugins.misc import paginate_modules
from utils import get_size, is_subscribed, temp
import re

logger = logging.getLogger(__name__)
BATCH_FILES = {}


@Client.on_message(filters.command("start") & filters.incoming & ~filters.edited)
async def start(client, message):
    if message.chat.type in ['group', 'supergroup']:
        if message.from_user.id in ADMINS:
            buttons = [
                [
                    InlineKeyboardButton('🤖 Updates', url='https://t.me/TeamEvamaria')
                ],
                [
                    InlineKeyboardButton('ℹ️ Help', url=f"https://t.me/{temp.U_NAME}?start=help"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply(
                script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title,
                                        temp.U_NAME,
                                        temp.B_NAME), reply_markup=reply_markup, parse_mode="html")
            await asyncio.sleep(2)
            # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
            if not await db.get_chat(message.chat.id):
                total = await client.get_chat_members_count(message.chat.id)
                await client.send_message(LOG_CHANNEL,
                                          script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total,
                                                                   "Unknown"))
                await db.add_chat(message.chat.id, message.chat.title)
            return
        else:
            btn = [[
                InlineKeyboardButton("⭕️ᴘᴍ ᴍᴇ ⭕️", url="https://t.me/testufsbot")
            ]]
            message.reply("Goto My PM, Then Click Start.. Here You Are Restricted By Admins...", reply_markup=btn)
            return
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL,
                                  script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('🔍 Search', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖 Updates', url='https://t.me/EvaMariaUpdates')
        ], [
            InlineKeyboardButton('ℹ️Help', callback_data='help'),
            InlineKeyboardButton('😊 About', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        btn = [
            [
                InlineKeyboardButton(
                    "🤖 Join Updates Channel", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            btn.append([InlineKeyboardButton(" 🔄 Try Again", callback_data=f"checksub#{message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**Please Join My Updates Channel to use this Bot!**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode="markdown"
        )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('🔍 Search', switch_inline_query_current_chat=''),
            InlineKeyboardButton('🤖 Updates', url='https://t.me/TeamEvamaria')
        ], [
            InlineKeyboardButton('ℹ️Help', callback_data='help'),
            InlineKeyboardButton('😊 About', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
        return

    file_id = message.command[1]
    # unique_id, f_id, file_ref, caption = await get_batch(file_id)

    files_ = await get_file_details(file_id)
    if not files_:
        sts = await message.reply("`⏳ Please Wait...`", parse_mode='markdown')
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try:
                with open(file) as file_data:
                    msgs = json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        await asyncio.sleep(1)
        await sts.delete()
        for msg in msgs:
            title = msg.get("title")
            size = get_size(int(msg.get("size", 0)))
            f_caption = msg.get("caption", "")
            file_type = msg.get("file_type")
            entities = msg.get("entities")

            if f_caption is None:
                f_caption = f"{title}"
            # f_caption = f_caption + f"\n\n<code>┈•••✿ @UniversalFilmStudio ✿•••┈\n\n💾 Size: {size}</code>"
            try:
                if file_type not in ["video", 'audio', 'document']:
                    await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        caption_entities=entities,
                    )
                else:
                    await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption + f"\n\n<code>┈•••✿ @UniversalFilmStudio ✿•••┈\n\n💾 Size: {size}</code>",
                        parse_mode="html",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        '🎭 ⭕️ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ⭕️', url="https://t.me/UFSChatBot"
                                    )
                                ]
                            ]
                        )
                    )
            except Exception as err:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, f"{str(err)}")
            await asyncio.sleep(0.5)
        return await message.reply(f"<b><a href='https://t.me/UniversalFilmStudio'>Thank For Using Me...</a></b>")

    # if unique_id:
    #     temp_msg = await message.reply("Please wait...")
    #     file_args = f_id.split("#")
    #     cap_args = caption.split("#")
    #     i = 0
    #     await asyncio.sleep(2)
    #     await temp_msg.delete()
    #     for b_file in file_args:
    #         f_caption = cap_args[i]
    #         if f_caption is None:
    #             f_caption = ""
    #         f_caption = f_caption + f"\n\n<code>┈•••✿</code> @UniversalFilmStudio <code>✿•••┈</code>"
    #         i += 1
    #         try:
    #             await client.send_cached_media(
    #                 chat_id=message.from_user.id,
    #                 file_id=b_file,
    #                 caption=f_caption,
    #                 parse_mode="html",
    #                 reply_markup=InlineKeyboardMarkup(
    #                     [
    #                         [
    #                             InlineKeyboardButton(
    #                                 '🎭 ⭕️ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ⭕️', url="https://t.me/UFSChatBot"
    #                             )
    #                         ]
    #                     ]
    #                 )
    #             )
    #         except Exception as err:
    #             return await message.reply(f"{str(err)}")
    #         await asyncio.sleep(1)
    #
    #     return await message.reply(f"<b><a href='https://t.me/UniversalFilmStudio'>Thank For Using Me...</a></b>")

    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    f_caption = f_caption + f"\n\n<code>┈•••✿ @UniversalFilmStudio ✿•••┈\n\n💾 Size: {size}</code>"
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        parse_mode="html",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        '🎭 ⭕️ ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ⭕️', url="https://t.me/UFSChatBot"
                    )
                ]
            ]
        )
    )


@Client.on_message(filters.command("help"))
async def help(client, message):
    first_name = message.from_user.first_name
    chat = message.chat.id  # type: Optional[Chat]
    args = message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:

        message.reply_text("Contact Me In PM To Get The List Of Possible Commands.",
                           reply_markup=InlineKeyboardMarkup(
                               [[InlineKeyboardButton(text="Help",
                                                      url="t.me/{}?start=help".format(
                                                          temp.U_NAME))]]))
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = "Here Is The Available Help For The **{}** Module:\n".format(HELPABLE[module].__mod_name__) \
               + HELPABLE[module].__help__
        send_help(client, chat.id, text,
                  InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data="help_back")]]))

    else:
        send_help(client, chat.id, script.HELP_STRINGS.format(first_name, "@lnc3f3r"))


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This Is Not Supported File Format')
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File Is Successfully Deleted From Database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_one({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })
        if result.deleted_count:
            await msg.edit('File Is Successfully Deleted From Database')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_one({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File Is Successfully Deleted From Database')
            else:
                await msg.edit('File Not Found In Database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer()
    await message.message.edit('Successfully Deleted All The Indexed Files.')


@Client.on_message(filters.command('restart') & filters.user(ADMINS))
async def upstream_repo(bot, message):
    os.system("git pull")
    time.sleep(10)
    os.execl(sys.executable, sys.executable, *sys.argv)
    msg = await message.reply("Your Bot 🤖 Is Updating & Restarting...", quote=True)
    time.sleep(10)
    await msg.delete()
    await message.delete()


@Bot.on_message(filters.command("bat"))
async def start111(client: Client, message):
    try:
        answer = await client.ask(message.chat.id, '*Send me your name:*', parse_mode='Markdown')
        await client.send_message(message.chat.id, f'Your name is: ')
    except Exception as err:
        await client.send_message(message.chat.id, f'Error is: {str(err)}')


def send_help(client, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    client.send_message(chat_id=chat_id,
                        text=text,
                        parse_mode="markdown",
                        reply_markup=keyboard)
