import re
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from plugins.helper_func import get_message_id
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL
from database.ia_filterdb import unpack_new_file_id
from database.connections_mdb import active_connection
from utils import temp
import re
import os
import json
import base64
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@Client.on_message(filters.command('getlink') & filters.user(ADMINS) & filters.incoming)
async def gen_link_s(client: Client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You Are Anonymous Admin. Use /connect {message.chat.id} In PM")
    chat_type = message.chat.type
    args = message.text.html.split(None, 1)

    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make Sure I'm Present In Your Group!!", quote=True)
                return
        else:
            await message.reply_text("I'm Not Connected To Any Groups!", quote=True)
            return

    elif chat_type in ["group", "supergroup"]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in ADMINS
    ):
        return

    while True:
        try:
            channel_message = await client.ask(text="Forward Message from the DB Channel (with Quotes)..\n"
                                                    "or Send the DB Channel Post link", chat_id=message.from_user.id,
                                               filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                                               timeout=60)
        except:
            return
        channel_id = channel_message.forward_from_chat.id
        try:
            channel = await client.get_chat(channel_id)
        except Exception as e:
            await channel_message.reply("❌ Error\n\nMake Sure Bot Is Admin In Forwarded Channel...", quote=True)
            return

        msg_id = await get_message_id(client, channel_message, channel_id)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not "
                                        "taken from DB Channel", quote=True)
            continue

    # replied = message.forward_message
    if not channel_message:
        return await message.reply('Forward Message from the DB Channel (with Quotes).')
    file_type = channel_message.media
    if file_type not in ["video", 'audio', 'document']:
        return await channel_message.reply("Send A Supported Media [video, audio, document]")

    outlist = []
    file_type = channel_message.media
    file = getattr(channel_message, file_type)
    file = {
        "file_id": file.file_id,
        "caption": f"<code>{channel_message.caption}</code>" if file_type in ["video", 'audio',
                                                                              'document'] else f"{channel_message.caption}",
        "title": getattr(file, "file_name", ""),
        "size": file.file_size,
        "file_type": file_type,
    }
    outlist.append(file)
    with open(f"singlemode_{channel_message.from_user.id}.json", "w+") as out:
        json.dump(outlist, out)
    post = await client.send_document(LOG_CHANNEL, f"singlemode_{channel_message.from_user.id}.json",
                                      file_name="Single.json",
                                      caption="⚠️Generated For File Store.")
    os.remove(f"singlemode_{channel_message.from_user.id}.json")
    file_id, ref = unpack_new_file_id(post.document.file_id)

    # file_id, ref = unpack_new_file_id((getattr(channel_message, file_type)).file_id)
    await channel_message.reply(f"Here is your Link:\nhttps://t.me/{temp.U_NAME}?start={file_id}")
    await channel_message.delete()
    await message.delete()


@Client.on_message(filters.command('batch') & filters.user(ADMINS) & filters.incoming)
async def gen_link_batch(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You Are Anonymous Admin. Use /connect {message.chat.id} In PM")
    chat_type = message.chat.type
    args = message.text.html.split(None, 1)

    if chat_type == "private":
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await bot.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make Sure I'm Present In Your Group!!", quote=True)
                return
        else:
            await message.reply_text("I'm Not Connected To Any Groups!", quote=True)
            return

    elif chat_type in ["group", "supergroup"]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await bot.get_chat_member(grp_id, userid)
    if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in ADMINS
    ):
        return

    while True:
        try:
            first_message = await bot.ask(text="Forward the First Message from DB Channel (with Quotes)..\n\n"
                                               "or Send the DB Channel Post Link", chat_id=message.from_user.id,
                                          filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                                          timeout=60)
        except:
            return
        first_channel_id = first_message.forward_from_chat.id
        try:
            channel = await bot.get_chat(first_channel_id)
        except Exception as e:
            await first_message.reply("❌ Error\n\nMake Sure Bot Is Admin In Forwarded Channel...", quote=True)
            return

        f_msg_id = await get_message_id(bot, first_message, first_channel_id)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken "
                                      "from DB Channel", quote=True)
            continue

    while True:
        try:
            second_message = await bot.ask(text="Forward the Last Message from DB Channel (with Quotes)..\n"
                                                "or Send the DB Channel Post link", chat_id=message.from_user.id,
                                           filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                                           timeout=60)
        except:
            return
        second_channel_id = second_message.forward_from_chat.id
        try:
            channel = await bot.get_chat(second_channel_id)
        except Exception as e:
            await second_message.reply("❌ Error\n\nMake Sure Bot Is Admin In Forwarded Channel...", quote=True)
            return

        if first_channel_id == second_channel_id:
            l_msg_id = await get_message_id(bot, second_message, second_channel_id)
            if l_msg_id:
                break
            else:
                await second_message.reply("❌ Error\n\nThis Forwarded Post Is Not From My DB Channel Or This "
                                           "Link Is Not Taken From DB Channel", quote=True)
                continue
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post Is Not From My First Forwarded Channel Or This "
                                       "Link Is Taken From DB Channel", quote=True)

    try:
        msgs_list = []
        c_msg = f_msg_id

        diff = l_msg_id - f_msg_id

        if diff <= 200:
            msgs = await bot.get_messages(first_channel_id, list(range(f_msg_id, l_msg_id + 1)))
            msgs_list += msgs
        else:
            c_msg = f_msg_id
            while True:
                new_diff = l_msg_id - c_msg
                if new_diff > 200:
                    new_diff = 200
                elif new_diff <= 0:
                    break
                msgs = await bot.get_messages(first_channel_id, list(range(c_msg, new_diff + 1)))
                msgs_list += msgs
        #######################################################################################
        # if " " not in message.text:
        #     return await message.reply("Use correct format.\nExample <code>/batch https://t.me/TeamEvamaria/10 "
        #                                "https://t.me/TeamEvamaria/20</code>.")
        # links = message.text.strip().split(" ")
        # if len(links) != 3:
        #     return await message.reply("Use correct format.\nExample <code>/batch https://t.me/TeamEvamaria/10 "
        #                                "https://t.me/TeamEvamaria/20</code>.")
        # _, first, last = links
        # regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        # match = regex.match(first)
        # if not match:
        #     return await message.reply('Invalid link')
        # f_chat_id = match.group(4)
        # f_msg_id = int(match.group(5))
        # if f_chat_id.isnumeric():
        #     f_chat_id = int(("-100" + f_chat_id))
        #
        # match = regex.match(last)
        # if not match:
        #     return await message.reply('Invalid link')
        # l_chat_id = match.group(4)
        # l_msg_id = int(match.group(5))
        # if l_chat_id.isnumeric():
        #     l_chat_id = int(("-100" + l_chat_id))
        #
        # if f_chat_id != l_chat_id:
        #     return await message.reply("Chat ids not matched.")
        # try:
        #     chat_id = (await bot.get_chat(f_chat_id)).id
        # except ChannelInvalid:
        #     return await message.reply(
        #         'This may be a private channel / group. Make me an admin over there to index the files.')
        # except (UsernameInvalid, UsernameNotModified):
        #     return await message.reply('Invalid Link specified.')
        # except Exception as e:
        #     return await message.reply(f'Errors - {e}')

        sts = await message.reply(
            "Generating Link For Your Message.\nThis May Take Time Depending Upon Number Of Messages")

        msgs_list = []
        c_msg = f_msg_id

        diff = l_msg_id - f_msg_id

        if diff <= 200:
            msgs = await bot.get_messages(first_channel_id, list(range(f_msg_id, l_msg_id + 1)))
            msgs_list += msgs
        else:
            c_msg = f_msg_id
            while True:
                new_diff = l_msg_id - c_msg
                if new_diff > 200:
                    new_diff = 200
                elif new_diff <= 0:
                    break
                msgs = await bot.get_messages(first_channel_id, list(range(c_msg, new_diff + 1)))
                msgs_list += msgs

        outlist = []
        # if chat_id in FILE_STORE_CHANNEL:
        #     string = f"{f_msg_id}_{l_msg_id}_{chat_id}"
        #     b_64 = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
        #     return await sts.edit(f"Here is your link https://t.me/{temp.U_NAME}?start=DSTORE-{b_64}")

        # file store without db channel
        for msg in msgs_list:
            if msg.empty or msg.service:
                continue
            if not msg.media:
                # only media messages supported.
                continue
            file_type = msg.media
            file = getattr(msg, file_type)
            file = {
                "file_id": file.file_id,
                "caption": f"<code>{msg.caption}</code>" if file_type in ["video", 'audio',
                                                                          'document'] else f"{msg.caption}",
                "title": getattr(file, "file_name", ""),
                "size": file.file_size,
                "file_type": file_type,
            }
            outlist.append(file)
        with open(f"batchmode_{message.from_user.id}.json", "w+") as out:
            json.dump(outlist, out)
        post = await bot.send_document(LOG_CHANNEL, f"batchmode_{message.from_user.id}.json", file_name="Batch.json",
                                       caption="⚠️Generated For File Store.")
        os.remove(f"batchmode_{message.from_user.id}.json")
        file_id, ref = unpack_new_file_id(post.document.file_id)
        link = f"https://t.me/{temp.U_NAME}?start={file_id}"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL",
                                                                   url=f'https://telegram.me/share/url?url={link}')]])
        await sts.edit(f"<b>Here is your link</b>\n\n{link}", reply_markup=reply_markup)
        await second_message.delete()
        await first_message.delete()
        await message.delete()
    except Exception as e:
        logger.exception(e)
        await second_message.edit(f'Error: {e}')


# import base64
# import logging
# import asyncio
#
# from bot import Bot
# from utils import temp
# from struct import pack
# from info import ADMINS
# from pyrogram.file_id import FileId
# from pyrogram import Client, filters
# from pyrogram.errors import FloodWait
# from database.batch_db import save_file
# from plugins.helper_func import get_message_id, encode
# from database.connections_mdb import active_connection
# from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# lock = asyncio.Lock()
#
#
# @Bot.on_message(filters.command('batch') & filters.incoming)
# async def batch_file(client: Client, message):
#     userid = message.from_user.id if message.from_user else None
#     if not userid:
#         return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
#     chat_type = message.chat.type
#     args = message.text.html.split(None, 1)
#
#     if chat_type == "private":
#         grpid = await active_connection(str(userid))
#         if grpid is not None:
#             grp_id = grpid
#             try:
#                 chat = await client.get_chat(grpid)
#                 title = chat.title
#             except:
#                 await message.reply_text("Make sure I'm present in your group!!", quote=True)
#                 return
#         else:
#             await message.reply_text("I'm not connected to any groups!", quote=True)
#             return
#
#     elif chat_type in ["group", "supergroup"]:
#         grp_id = message.chat.id
#         title = message.chat.title
#
#     else:
#         return
#
#     st = await client.get_chat_member(grp_id, userid)
#     if (
#             st.status != "administrator"
#             and st.status != "creator"
#             and str(userid) not in ADMINS
#     ):
#         return
#
#     while True:
#         try:
#             first_message = await client.ask(text="Forward the First Message from DB Channel (with Quotes)..\n\n"
#                                                   "or Send the DB Channel Post Link", chat_id=message.from_user.id,
#                                              filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
#                                              timeout=60)
#         except:
#             return
#         first_channel_id = first_message.forward_from_chat.id
#         try:
#             channel = await client.get_chat(first_channel_id)
#         except Exception as e:
#             await first_message.reply("❌ Error\n\nMake Sure Bot Is Admin In Forwarded Channel...", quote=True)
#             return
#
#         f_msg_id = await get_message_id(client, first_message, first_channel_id)
#         if f_msg_id:
#             break
#         else:
#             await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken "
#                                       "from DB Channel", quote=True)
#             continue
#
#     while True:
#         try:
#             second_message = await client.ask(text="Forward the Last Message from DB Channel (with Quotes)..\n"
#                                                    "or Send the DB Channel Post link", chat_id=message.from_user.id,
#                                               filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
#                                               timeout=60)
#         except:
#             return
#         second_channel_id = second_message.forward_from_chat.id
#         try:
#             channel = await client.get_chat(second_channel_id)
#         except Exception as e:
#             await second_message.reply("❌ Error\n\nMake Sure Bot Is Admin In Forwarded Channel...", quote=True)
#             return
#
#         if first_channel_id == second_channel_id:
#             s_msg_id = await get_message_id(client, second_message, second_channel_id)
#             if s_msg_id:
#                 break
#             else:
#                 await second_message.reply("❌ Error\n\nThis Forwarded Post Is Not From My DB Channel Or This "
#                                            "Link Is Not Taken From DB Channel", quote=True)
#                 continue
#         else:
#             await second_message.reply("❌ Error\n\nthis Forwarded Post Is Not From My First Forwarded Channel Or This "
#                                        "Link Is Taken From DB Channel", quote=True)
#
#     string = f"get-{f_msg_id}-{s_msg_id}-{abs(second_channel_id)}"
#     base64_string = await encode(string)
#     link = f"https://t.me/{temp.U_NAME}?start={base64_string}"
#
#     async with lock:
#         try:
#             total = s_msg_id + 1
#             current = f_msg_id
#             file_id = ''
#             file_ref = ''
#             caption = ''
#             cap = None
#             while current < total:
#                 try:
#                     message = await client.get_messages(chat_id=second_channel_id, message_ids=current, replies=0)
#                 except FloodWait as e:
#                     await asyncio.sleep(e.x)
#                     message = await client.get_messages(
#                         second_channel_id,
#                         current,
#                         replies=0
#                     )
#                 except Exception as e:
#                     logger.exception(e)
#
#                 try:
#                     for file_type in ("document", "video", "audio"):
#                         media = getattr(message, file_type, None)
#                         if media is not None:
#                             break
#                         else:
#                             continue
#                     media.file_type = file_type
#                     media.caption = message.caption
#
#                     # TODO: Find better way to get same file_id for same media to avoid duplicates
#                     _id, _ref = unpack_new_file_id(media.file_id)
#                     file_id = file_id + _id + "#"
#                     file_ref = file_ref + _ref + "#"
#                     # file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
#                     cap = media.caption.html if media.caption else None
#                     caption = caption + cap + "#"
#                 except Exception as e:
#                     if "NoneType" in str(e):
#                         logger.warning(
#                             "Skipping deleted / Non-Media messages (if this continues for long, "
#                             "use /setskip to set a skip number)")
#                     else:
#                         logger.exception(e)
#                 current += 1
#
#             file_id = file_id[:-1]
#             file_ref = file_ref[:-1]
#             caption = caption[:-1]
#             aynav, vnay = await save_file(base64_string, file_id, file_ref, caption)
#
#         except Exception as e:
#             logger.exception(e)
#             await second_message.edit(f'Error: {e}')
#         else:
#             reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL",
#                                                                        url=f'https://telegram.me/share/url?url={link}')]])
#             await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True,
#                                             reply_markup=reply_markup)
#
#
# @Bot.on_message(filters.command('getlink') & filters.incoming)
# async def batch_single_file(client: Client, message):
#     userid = message.from_user.id if message.from_user else None
#     if not userid:
#         return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
#     chat_type = message.chat.type
#     args = message.text.html.split(None, 1)
#
#     if chat_type == "private":
#         grpid = await active_connection(str(userid))
#         if grpid is not None:
#             grp_id = grpid
#             try:
#                 chat = await client.get_chat(grpid)
#                 title = chat.title
#             except:
#                 await message.reply_text("Make sure I'm present in your group!!", quote=True)
#                 return
#         else:
#             await message.reply_text("I'm not connected to any groups!", quote=True)
#             return
#
#     elif chat_type in ["group", "supergroup"]:
#         grp_id = message.chat.id
#         title = message.chat.title
#
#     else:
#         return
#
#     st = await client.get_chat_member(grp_id, userid)
#     if (
#             st.status != "administrator"
#             and st.status != "creator"
#             and str(userid) not in ADMINS
#     ):
#         return
#
#     while True:
#         try:
#             channel_message = await client.ask(text="Forward Message from the DB Channel (with Quotes)..\n"
#                                                     "or Send the DB Channel Post link", chat_id=message.from_user.id,
#                                                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
#                                                timeout=60)
#         except:
#             return
#         channel_id = channel_message.forward_from_chat.id
#         try:
#             channel = await client.get_chat(channel_id)
#         except Exception as e:
#             await channel_message.reply("❌ Error\n\nMake Sure Bot Is Admin In Forwarded Channel...", quote=True)
#             return
#
#         msg_id = await get_message_id(client, channel_message, channel_id)
#         if msg_id:
#             break
#         else:
#             await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not "
#                                         "taken from DB Channel", quote=True)
#             continue
#
#     string = f"get-{msg_id}-{abs(channel_id)}"
#     base64_string = await encode(string)
#     link = f"https://t.me/{temp.U_NAME}?start={base64_string}"
#
#     async with lock:
#         try:
#             total = msg_id + 1
#             current = msg_id
#             file_id = ''
#             file_ref = ''
#             caption = ''
#             cap = None
#             while current < total:
#                 try:
#                     message = await client.get_messages(chat_id=channel_id, message_ids=current, replies=0)
#                 except FloodWait as e:
#                     await asyncio.sleep(e.x)
#                     message = await client.get_messages(
#                         channel_id,
#                         current,
#                         replies=0
#                     )
#                 except Exception as e:
#                     logger.exception(e)
#
#                 try:
#                     for file_type in ("document", "video", "audio"):
#                         media = getattr(message, file_type, None)
#                         if media is not None:
#                             break
#                         else:
#                             continue
#                     media.file_type = file_type
#                     media.caption = message.caption
#
#                     # TODO: Find better way to get same file_id for same media to avoid duplicates
#                     _id, _ref = unpack_new_file_id(media.file_id)
#                     file_id = file_id + _id + "#"
#                     file_ref = file_ref + _ref + "#"
#                     # file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
#                     cap = media.caption.html if media.caption else None
#                     caption = caption + cap + "#"
#                 except Exception as e:
#                     if "NoneType" in str(e):
#                         logger.warning(
#                             "Skipping deleted / Non-Media messages (if this continues for long, "
#                             "use /setskip to set a skip number)")
#                     else:
#                         logger.exception(e)
#                 current += 1
#
#             file_id = file_id[:-1]
#             file_ref = file_ref[:-1]
#             caption = caption[:-1]
#             aynav, vnay = await save_file(base64_string, file_id, file_ref, caption)
#
#         except Exception as e:
#             logger.exception(e)
#             await channel_message.edit(f'Error: {e}')
#         else:
#             reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL",
#                                                                        url=f'https://telegram.me/share/url?url={link}')]])
#             await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True,
#                                            reply_markup=reply_markup)
#
#
# @Bot.on_message(filters.command('dellink') & filters.incoming)
# async def delete_batch(client: Client, message):
#     test = message.text
#
#
# def encode_file_id(s: bytes) -> str:
#     r = b""
#     n = 0
#
#     for i in s + bytes([22]) + bytes([4]):
#         if i == 0:
#             n += 1
#         else:
#             if n:
#                 r += b"\x00" + bytes([n])
#                 n = 0
#
#             r += bytes([i])
#
#     return base64.urlsafe_b64encode(r).decode().rstrip("=")
#
#
# def encode_file_ref(file_ref: bytes) -> str:
#     return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")
#
#
# def unpack_new_file_id(new_file_id):
#     """Return file_id, file_ref"""
#     decoded = FileId.decode(new_file_id)
#     file_id = encode_file_id(
#         pack(
#             "<iiqq",
#             int(decoded.file_type),
#             decoded.dc_id,
#             decoded.media_id,
#             decoded.access_hash
#         )
#     )
#     file_ref = encode_file_ref(decoded.file_reference)
#     return file_id, file_ref


__help__ = """
 - /batch: Generate Your Batch File Link
 
 Note:- I'm Should Be Admin In Your DB Channels & Your Movie Groups.
 Connect Me From Your Group By Using /connect Command.
 
 Send /batch Command, And Follow The Instructions.
"""

__mod_name__ = "Batch"
