import logging
from pyrogram import Client, filters, dispatcher
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, get_msg_type, Types, markdown_parser
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import BadRequest, FloodWait, UserIsBlocked, InputUserDeactivated, UserIsBot, PeerIdInvalid
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
# https://t.me/GetTGLink/4178
async def verupikkals(bot, message):
    all_users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Please Wait, Broadcasting Is Starting Soon...', quote=True
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0

    i = 0
    b = 0
    ia = 0
    ub = 0

    success = 0
    async for user in all_users:
        text, data_type, content, buttons = get_msg_type(b_msg)
        i += 1
        if not user['id'] in ADMINS:
            try:
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`",
                                    parse_mode="markdown")
                success += 1
                await send_broadcast_message(user['id'], text, data_type, content, buttons, bot, message)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`",
                                    parse_mode="markdown")
                success += 1
                await send_broadcast_message(user['id'], text, data_type, content, buttons, bot, message)
            except UserIsBlocked:
                b += 1
                logging.info(f"{user['id']} - Blocked the bot.")
                blocked += 1
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`",
                                    parse_mode="markdown")
                pass
            except InputUserDeactivated:
                ia += 1
                await db.delete_user(int(user['id']))
                deleted += 1
                logging.info(f"{user['id']} - Removed from Database, Since Deleted Account.")
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`",
                                    parse_mode="markdown")
                pass
            except UserIsBot:
                ub += 1
                await sts.edit_text(f"**Broadcast Successfully Completed** `{i}/{total_users}`"
                                    f"\n**Total Blocked By User** `{b}`"
                                    f"\n**Total Inactive User** `{ia}`"
                                    f"\n**Total Bot As User** `{ub}`",
                                    parse_mode="markdown")
                pass
            except PeerIdInvalid:
                await db.delete_user(int(user['id']))
                logging.info(f"{user['id']} - PeerIdInvalid")
                pass
            except Exception as err:
                logging.info(f"{str(err)}")
                return

        # pti, sh = await broadcast_messages(int(user['id']), b_msg)
        # if pti:
        #     success += 1
        # elif pti == False:
        #     if sh == "Bocked":
        #         blocked += 1
        #     elif sh == "Deleted":
        #         deleted += 1
        #     elif sh == "Error":
        #         failed += 1
            done += 1
            # await asyncio.sleep(2)
            # if not done % 5:
            #     await sts.edit_text(
            #         f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit_text(
        f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")


async def send_broadcast_message(user_id, text, data_type, content, buttons, client, message):
    if message.from_user.id in ADMINS:
        if data_type != Types.TEXT and data_type != Types.BUTTON_TEXT and \
                data_type != Types.PHOTO and data_type != Types.BUTTON_PHOTO:
            if data_type == 2:
                await client.send_sticker(chat_id=user_id, sticker=content)
            elif data_type == 3:
                await client.send_document(chat_id=user_id, document=content)
            elif data_type == 6:
                await client.send_audio(chat_id=user_id, audio=content)
            elif data_type == 7:
                await client.send_voice(chat_id=user_id, voice=content)
            elif data_type == 8:
                await client.send_video(chat_id=user_id, video=content)
            return
        # else, move on

        if data_type != 0:
            # buttons = get_schedule_buttons(job.s_job_name)
            keyb = build_url_keyboard(buttons)
        else:
            keyb = []

        keyboard = InlineKeyboardMarkup(keyb)

        if data_type == Types.BUTTON_PHOTO:
            await client.send_photo(user_id, content, caption=text, reply_markup=keyboard, parse_mode="markdown")
        elif data_type == Types.PHOTO:
            await client.send_photo(user_id, content, caption=text, parse_mode="markdown")
        else:
            # send(client, job.s_chat_id, msg_text, keyboard, "Hey Dear, how are you?")
            try:
                if len(keyboard.inline_keyboard) > 0:
                    await client.send_message(chat_id=user_id, text=text, parse_mode="markdown",
                                              reply_markup=keyboard,
                                              disable_web_page_preview=True)
                else:
                    await client.send_message(chat_id=user_id, text=text, parse_mode="markdown",
                                              disable_web_page_preview=True)
            except IndexError:
                await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                         "\nNote: The Current Message Was "
                                                         "Invalid Due To Markdown Issues. Could Be "
                                                         "Due To The User's Name."),
                                         parse_mode="markdown",
                                         disable_web_page_preview=True)
            except KeyError:
                await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                         "\nNote: The Current Message Is "
                                                         "Invalid Due To An Issue With Some Misplaced "
                                                         "Messages. Please Update"),
                                         parse_mode="markdown",
                                         disable_web_page_preview=True)
            except UserIsBlocked:
                pass
            except InputUserDeactivated:
                pass
            except UserIsBot:
                pass
            except BadRequest as excp:
                if excp.MESSAGE == "Button_url_invalid":
                    await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                             "\nNote: The Current Message Has An Invalid Url "
                                                             "In One Of Its Buttons. Please Update."),
                                             parse_mode="markdown")
                elif excp.MESSAGE == "Unsupported url protocol":
                    await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                             "\nNote: The Current Message Has Buttons Which "
                                                             "Use Url Protocols That Are Unsupported By "
                                                             "Telegram. Please Update."),
                                             parse_mode="markdown")
                elif excp.MESSAGE == "Wrong url host":
                    await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                             "\nNote: The Current Message Has Some Bad Urls. "
                                                             "Please Update."),
                                             parse_mode="markdown")
                    logging.warning(text)
                    logging.warning(keyboard)
                    logging.exception("Could Not Parse! Got Invalid Url Host Errors")
                else:
                    await message.reply_text(markdown_parser("Hey Dear, how are you?" +
                                                             "\nNote: An Error Occured When Sending The "
                                                             "Custom Message. Please Update."),
                                             parse_mode="markdown")
                    logging.exception(excp.MESSAGE)
    else:
        await message.reply_text("Who The Hell You Are To Send This Command To Me...😡")
        return


def build_url_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], url=btn[1]))
        else:
            keyb.append([InlineKeyboardButton(btn[0], url=btn[1])])

    return keyb


__help__ = """
*Admin only:*
 - /broadcast Broadcast Your Message To Users...
 
 Broadcasting The Message To All Subscribed Users.
 
 Support Message Format, Image, Video, Stickers, Text, Image With Buttons, Text With Buttons.
 
 Format For Text With Buttons:
    Hello Dear How Are You! You Can Join My Channel.
    [Join Here](buttonurl://t.me/M76Links)
"""

__mod_name__ = "Broadcast"
