import re
import ast
import asyncio
import logging
import random
import pyrogram

from info import *
from Script import script
from pyrogram import Client, filters
from database.users_chats_db import db
from plugins.misc import paginate_modules
from plugins.helper_func import TimeFormatter
from database.filters_mdb import del_all, find_filter, get_filters
from utils import get_size, is_subscribed, get_poster, search_gagala, temp
from database.ia_filterdb import Media, get_file_details, get_search_results
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid, BadRequest
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from database.settings_db import sett_db
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & ~filters.edited & filters.incoming)
async def give_filter(client, message):
    group_id = message.chat.id
    chat_type = message.sender_chat.type if message.sender_chat else None
    name = message.text

    if chat_type in ["channel"]:
        text = f"""
#DETECT_SENDER_AS_CHANNEL

**CHANNEL: {message.sender_chat.title} ({message.sender_chat.id})** 
`CHAT: {message.chat.title} ({message.chat.id})`
**MESSAGE: You Cannot Request Via Channel**"""
        chat_channel = await message.reply_text(text, parse_mode="md", quote=True)
        await asyncio.sleep(2)
        await chat_channel.delete()
        await message.delete()
        return

    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            await check_manual_filter(client, group_id, keyword, message, 0)
            return
            # reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
            #
            # if reply_text:
            #     reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")
            #
            # if btn is not None:
            #     try:
            #         if fileid == "None":
            #             if btn == "[]":
            #                 await message.reply_text(reply_text, disable_web_page_preview=True)
            #             else:
            #                 button = eval(btn)
            #                 await message.reply_text(
            #                     reply_text,
            #                     disable_web_page_preview=True,
            #                     reply_markup=InlineKeyboardMarkup(button)
            #                 )
            #         elif btn == "[]":
            #             await message.reply_cached_media(
            #                 fileid,
            #                 caption=reply_text or ""
            #             )
            #         else:
            #             button = eval(btn)
            #             await message.reply_cached_media(
            #                 fileid,
            #                 caption=reply_text or "",
            #                 reply_markup=InlineKeyboardMarkup(button)
            #             )
            #     except Exception as e:
            #         logger.exception(e)
            #     break
    else:
        await auto_filter(client, message)


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    ad_user = query.from_user.id
    if int(ad_user) in ADMINS:
        pass
    elif int(req) not in [query.from_user.id, 0]:
        return await query.answer(
            "കാര്യമൊക്കെ കൊള്ളാം, പക്ഷേ, ഇത്‌ നിങ്ങളുടേതല്ല.;\nNice Try! But, This Was Not Your Request, Request Yourself;",
            show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You Are Using One Of My Old Messages, Please Send The Request Again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    settings = await sett_db.get_settings(str(query.message.chat.id))
    if settings is not None:
        SINGLE_BUTTON = settings["button"]
        SPELL_CHECK_REPLY = settings["spell_check"]
        IMDB = settings["imdb"]

    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] - 🎬 {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {round(int(offset) / 10) + 1} / {round(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )

    btn.insert(0, [
        InlineKeyboardButton("📺 𝕊𝕖𝕣𝕚𝕖𝕤 𝕌𝕡𝕕𝕒𝕥𝕖𝕤 📺", url="https://t.me/TvSeriesLand4U")
    ])

    btn.insert(0, [
        InlineKeyboardButton("🎬 𝕄𝕠𝕧𝕚𝕖 🎬", url="https://t.me/onlymovie76"),
        InlineKeyboardButton("🗞️ 𝕆𝕋𝕋 𝕌𝕡𝕕𝕒𝕥𝕖𝕤 🗞️", url="https://t.me/M76Links")
    ])
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    ad_user = query.from_user.id
    if int(ad_user) in ADMINS:
        pass
    elif int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("കാര്യമൊക്കെ കൊള്ളാം, പക്ഷേ, ഇത്‌ നിങ്ങളുടേതല്ല.;\nNice Try! But, This Was Not Your Request, Request Yourself;",
                                  show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.message_id)
    if not movies:
        return await query.answer("You Are Clicking On An Old Button Which Is Expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking For Series In Database...')
    files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await auto_filter(bot, query, k)
    else:
        k = await query.message.edit('This Series Not Found In DataBase')
        await asyncio.sleep(10)
        await query.message.reply_to_message.delete()
        await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    first_name = query.from_user.first_name
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    help_match = re.match(r"help_", query.data)
    close_match = re.match(r"close_btn", query.data)

    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make Sure I'm Present In Your Group!!", quote=True)
                    return
            else:
                await query.message.edit_text(
                    "I'm Not Connected To Any Groups!\nCheck /connections Or Connect To Any Groups",
                    quote=True
                )
                return

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == "creator") or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You Need To Be Group Owner Or An Auth User To Do That!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == "creator") or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Thats not for you!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode="md"
        )
        return
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text('Some error occured!!', parse_mode="md")
        return
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text(
                f"Some error occured!!",
                parse_mode="md"
            )
        return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occured!!",
                parse_mode="md"
            )
        return
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There Are No Active Connections!! Connect To Some Groups First.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        user = query.message.reply_to_message.from_user.id
        ad_user = query.from_user.id

        settings = await sett_db.get_settings(str(query.message.chat.id))
        if settings is not None:
            SINGLE_BUTTON = settings["button"]
            SPELL_CHECK_REPLY = settings["spell_check"]
            P_TTI_SHOW_OFF = settings["botpm"]
            IMDB = settings["imdb"]

        if FILE_PROTECT.get(query.from_user.id):
            del FILE_PROTECT[query.from_user.id]
        FILE_PROTECT[query.from_user.id] = str(query.message.chat.id)
        if int(ad_user) in ADMINS:
            pass
        elif int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(
                "കാര്യമൊക്കെ കൊള്ളാം, പക്ഷേ, ഇത്‌ നിങ്ങളുടേതല്ല.;\nNice Try! But, This Was Not Your Request, Request Yourself;",
                show_alert=True)

        if not files_:
            return await query.answer('No such file exist.')
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
        f_caption = f_caption + f"\n\n<code> ✰ @TvSeriesLand4U ✰\n\n🚀 Size: {size}</code>"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            elif P_TTI_SHOW_OFF:     # P_TTI_SHOW_OFF
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    parse_mode="html",
                    protect_content=settings["file_secure"] if settings["file_secure"] else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    '📺 Wᴇʙ Sᴇʀɪᴇs', url="https://t.me/TvSeriesLand4U"
                                ),
                                InlineKeyboardButton(
                                    '🎬 ᴍᴏᴠɪᴇs', url="https://t.me/onlymovie76"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    '🗞️ Updates', url="https://t.me/M76Links"
                                )
                            ]
                        ]
                    )
                )
                await query.answer('Check My PM, I Have Sent Files In Your PM', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock Me Dude!', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Over Smart 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
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
            f_caption = f"{title}"
        f_caption = f_caption + f"\n\n<code>✰ @TvSeriesLand4U ✰\n\n🚀 Size: {size}</code>"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            parse_mode="html",
            protect_content=False,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            '📺 Wᴇʙ Sᴇʀɪᴇs', url="https://t.me/TvSeriesLand4U"
                        ),
                        InlineKeyboardButton(
                            '🎬 ᴍᴏᴠɪᴇs', url="https://t.me/onlymovie76"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            '🗞️ Updates', url="https://t.me/M76Links"
                        )
                    ]
                ]
            )
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [
            [
                InlineKeyboardButton('🔍 Search', switch_inline_query_current_chat=''),
                InlineKeyboardButton('🚀 Updates', url='https://t.me/TvSeriesLand4U_Updates')
            ],
            [
                InlineKeyboardButton('ℹ Help', callback_data='help'),
                InlineKeyboardButton('😊 About', callback_data='about')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "help":
        # if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
        await query.message.edit_text(
            text=script.HELP_STRINGS.format(query.from_user.mention, "@lnc3f3r"),
            parse_mode="html",
            reply_markup=keyboard)

        # buttons = [
        #     [
        #         InlineKeyboardButton('Manual Filter', callback_data='manuelfilter'),
        #         InlineKeyboardButton('Auto Filter', callback_data='autofilter')
        #     ],
        #     [
        #         InlineKeyboardButton('Connection', callback_data='coct'),
        #         InlineKeyboardButton('Extra Mods', callback_data='extra')
        #     ],
        #     [
        #         InlineKeyboardButton('🏠 Home', callback_data='start'),
        #         InlineKeyboardButton('🔮 Status', callback_data='stats')
        #     ]
        # ]
        # reply_markup = InlineKeyboardMarkup(buttons)
        # await query.message.edit_text(
        #     text=script.HELP_TXT.format(query.from_user.mention),
        #     reply_markup=reply_markup,
        #     parse_mode='html'
        # )
    elif query.data == "about":
        buttons = [
            [
                InlineKeyboardButton('🗞️ Updates', url='https://t.me/M76Links'),
                InlineKeyboardButton('♥️ Source', callback_data='source')
            ],
            [
                InlineKeyboardButton('🏠 Home', callback_data='start'),
                InlineKeyboardButton('🔐 Close', callback_data='close_data')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "source":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='about')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "manuelfilter":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
                InlineKeyboardButton('⏹️ Buttons', callback_data='button')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "button":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='manuelfilter')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "autofilter":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "coct":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "extra":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
                InlineKeyboardButton('👮‍♂️ Admin', callback_data='admin')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "admin":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='extra')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "stats":
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
                InlineKeyboardButton('♻️', callback_data='rfrsh')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode='html'
        )
        await asyncio.sleep(5)
        await client.request_callback_answer(query.message.chat.id, query.message.message_id, "help")
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [
            [
                InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
                InlineKeyboardButton('♻️', callback_data='rfrsh')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "imdb":
        i, movie = query.data.split('#')
        imdb = await get_poster(query=movie, id=True)
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{imdb.get('title')}",
                    url=imdb['url'],
                )
            ]
        ]
        if imdb:
            caption = IMDB_TEMPLATE.format(
                query=imdb['title'],
                title=imdb['title'],
                votes=imdb['votes'],
                aka=imdb["aka"],
                seasons=imdb["seasons"],
                box_office=imdb['box_office'],
                localized_title=imdb['localized_title'],
                kind=imdb['kind'],
                imdb_id=imdb["imdb_id"],
                cast=imdb["cast"],
                runtime=imdb["runtime"],
                countries=imdb["countries"],
                certificates=imdb["certificates"],
                languages=imdb["languages"],
                director=imdb["director"],
                writer=imdb["writer"],
                producer=imdb["producer"],
                composer=imdb["composer"],
                cinematographer=imdb["cinematographer"],
                music_team=imdb["music_team"],
                distributors=imdb["distributors"],
                release_date=imdb['release_date'],
                year=imdb['year'],
                genres=imdb['genres'],
                poster=imdb['poster'],
                plot=imdb['plot'],
                rating=imdb['rating'],
                url=imdb['url'],
                **locals()
            )
        else:
            caption = "No Results"
        if imdb.get('poster'):
            try:
                await query.message.reply_photo(photo=imdb['poster'], caption=caption,
                                                reply_markup=InlineKeyboardMarkup(btn))
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                await query.message.reply_photo(photo=imdb['poster'], caption=caption,
                                                reply_markup=InlineKeyboardMarkup(btn))
            except Exception as e:
                logger.exception(e)
                await query.message.reply(caption, reply_markup=InlineKeyboardMarkup(btn),
                                          disable_web_page_preview=False)
            await query.message.delete()
        else:
            await query.message.edit(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=False)
        await query.answer()
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id, time = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return

        if set_type == "delete":
            time = int(time) + 30
            await sett_db.update_settings(grp_id, set_type, True if (0 < int(time) <= 180) else False,
                                          time if (0 < int(time) <= 180) else 0)
        else:
            await sett_db.update_settings(grp_id, set_type, False if status == "True" else True, 0)

        settings = await sett_db.get_settings(str(grp_id))

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Auto Delete',
                                         callback_data=f'setgs#delete#{settings["auto_delete"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton(f'{settings["delete_time"]} Sec' if settings["auto_delete"] else '❌ No',
                                         callback_data=f'setgs#delete#{settings["auto_delete"]}#{str(grp_id)}#{settings["delete_time"]}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}#{settings["delete_time"]}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}#{settings["delete_time"]}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)

    # ######################### MODULE HELP START #############################################################
    try:
        if mod_match:
            module = mod_match.group(1)
            text = "Here is the help for the **{}** module:\n".format(HELPABLE[module].__mod_name__) \
                   + HELPABLE[module].__help__
            await query.message.edit_text(text=text,
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(
                                              [[InlineKeyboardButton(text="Back", callback_data="help_back")]]))

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(
                                              paginate_modules(curr_page - 1, HELPABLE, "help")))

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(
                                              paginate_modules(next_page + 1, HELPABLE, "help")))

        elif back_match:
            await query.message.edit_text(text=script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))

        elif help_match:
            await query.message.edit_text(text=script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))
        elif close_match:
            await query.message.edit_text(text=script.HELP_STRINGS.format(first_name, "@lnc3f3r"),
                                          parse_mode="markdown",
                                          reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")))

        # ensure no spinny white circle
        await client.answer_callback_query(query.id)
        # await query.message.delete()
        # bot.delete_message(update.effective_chat.id, update.effective_message.message_id - 1)
    except BadRequest as excp:
        if excp.message == "Message Is Not Modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message Can't Be Deleted":
            pass
        else:
            logging.exception("Exception In Help Buttons. %s", str(query.data))

    # ######################### MODULE HELP END #############################################################


async def check_manual_filter(client, group_id, keyword, message, msg):
    reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
    # if bool(msg.message.reply_to_message):
    #     message = msg.message.reply_to_message
    # else:
    #     message = msg

    if reply_text:
        reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

    settings = await sett_db.get_settings(str(group_id))
    if settings is not None:
        AUTO_DELETE = settings["auto_delete"]
        DELETE_TIME = settings["delete_time"]

    if AUTO_DELETE:
        reply_text = reply_text + f"<b><u>Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ Dᴇʟᴇᴛᴇ Tʜɪs Rᴇϙᴜᴇsᴛ Aғᴛᴇʀ {TimeFormatter(int(DELETE_TIME) * 1000)}</u></b>"

    if btn is not None:
        try:
            if FILE_PROTECT.get(message.from_user.id):
                del FILE_PROTECT[message.from_user.id]
                del FILE_PROTECT['631110062']
            FILE_PROTECT['631110062'] = str(message.chat.id)
            FILE_PROTECT[message.from_user.id] = str(message.chat.id)

            if fileid == "None":
                if btn == "[]":
                    d_msg = await message.reply_text(reply_text, disable_web_page_preview=True)

                # if AUTO_DELETE:
                #     await asyncio.sleep(int(DELETE_TIME))
                #     await message.delete()
                #     await d_msg.delete()
                else:
                    button = eval(btn)
                    d_msg = await message.reply_text(
                        reply_text,
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(button)
                    )

                if int(msg) > 0:
                    await client.delete_messages(chat_id=group_id, message_ids=int(msg))
                    # await msg.message.delete()

                if AUTO_DELETE:
                    await asyncio.sleep(int(DELETE_TIME))
                    await message.delete()
                    await d_msg.delete()
            elif btn == "[]":
                d_msg = await message.reply_cached_media(
                    fileid,
                    caption=reply_text or ""
                )

                if int(msg) > 0:
                    await client.delete_messages(chat_id=group_id, message_ids=int(msg))
                    # await msg.message.delete()

                if AUTO_DELETE:
                    await asyncio.sleep(int(DELETE_TIME))
                    await message.delete()
                    await d_msg.delete()
            else:
                button = eval(btn)
                d_msg = await message.reply_cached_media(
                    fileid,
                    caption=reply_text or "",
                    reply_markup=InlineKeyboardMarkup(button)
                )

                if int(msg) > 0:
                    await client.delete_messages(chat_id=group_id, message_ids=int(msg))
                    # await msg.message.delete()

                if AUTO_DELETE:
                    await asyncio.sleep(int(DELETE_TIME))
                    await message.delete()
                    await d_msg.delete()
        except Exception as e:
            logger.exception(e)


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await sett_db.get_settings(str(message.chat.id))
        if settings is not None:
            SINGLE_BUTTON = settings["button"]
            SPELL_CHECK_REPLY = settings["spell_check"]
            IMDB = settings["imdb"]
            AUTO_DELETE = settings["auto_delete"]
            DELETE_TIME = settings["delete_time"]
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return

        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if SPELL_CHECK_REPLY:
                    return await advantage_spell_chok(client, msg)
                else:
                    Send_message = await client.send_video(
                        chat_id=msg.chat.id,
                        video="https://telegra.ph/file/1fbdc1703b58c5c0ed242.mp4",
                        caption=f"Couldn't Find This Movie.Please Try Again Or Search On Our "
                                f"<b><a href='https://t.me/onlymovie76'>Group</a></b>. \n\n"
                                f"ഈ സീരീസ്ന്റ് ഒറിജിനൽ പേര് പോയി കണ്ടെത്തി അതുപോലെ ഇവിടെ കൊടുക്കുക 🥺",
                        parse_mode="html",
                        reply_to_message_id=msg.message_id
                    )
                    await asyncio.sleep(15)  # in seconds
                    await Send_message.delete()
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        settings = await sett_db.get_settings(str(message.chat.id))
        if settings is not None:
            SINGLE_BUTTON = settings["button"]
            SPELL_CHECK_REPLY = settings["spell_check"]
            IMDB = settings["imdb"]
            AUTO_DELETE = settings["auto_delete"]
            DELETE_TIME = settings["delete_time"]

        search, files, offset, total_results = spoll
        keywords = await get_filters(msg.message.chat.id)
        for keyword in reversed(sorted(keywords, key=len)):
            pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
            if re.search(pattern, search, flags=re.IGNORECASE):
                await check_manual_filter(client, message.chat.id, keyword, message, msg.message.message_id)
                # await msg.message.delete()
                return

    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] - 🎬 {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]

        for file in files:
            if any(x in str(file.file_name) for x in ["PreDVD", "Scr"]):
                Quality = "List Contains PreDVDRip/ScrRip"
                break
            else:
                Quality = "HDRip/WebRip"

    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'files#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

        for file in files:
            if any(x in str(file.file_name) for x in ["PreDVD", "Scr"]):
                Quality = "List Contains PreDVDRip/ScrRip"
                break
            else:
                Quality = "HDRip/WebRip"

    if offset != "":
        key = f"{message.chat.id}-{message.message_id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{round(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )

    btn.insert(0, [
        InlineKeyboardButton("📺 Wᴇʙ Sᴇʀɪᴇs", url="https://t.me/TvSeriesLand4U")
    ])
    btn.insert(0, [
        InlineKeyboardButton("🗞️ Updates", url="https://t.me/M76Links"),
        InlineKeyboardButton("🎬 ɴᴇᴡ ᴍᴏᴠɪᴇs", url="https://t.me/onlymovie76")
    ])
    imdb = await get_poster(search, file=(files[0]).file_name) if IMDB else None
    query_by = f"<b>ɴᴏ ᴏғ ғɪʟᴇs :</b> <code><b><i>{total_results}</i></b></code>\n" \
               f"<b>ʏᴏᴜʀ ϙᴜᴇʀʏ :</b> <code><b><i>{search}</i></b></code>\n" \
               f"<b>Qᴜᴀʟɪᴛʏ :</b> <code><b><i>{Quality}</i></b></code>\n" \
               f"<b>ʀᴇϙᴜᴇsᴛᴇᴅ ʙʏ :</b> <b><spoiler>{msg.from_user.first_name}</spoiler></b>"
    if AUTO_DELETE:
        query_by = query_by + f"\n\n<b><u>Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ Dᴇʟᴇᴛᴇ Tʜɪs Rᴇϙᴜᴇsᴛ Aғᴛᴇʀ {TimeFormatter(int(DELETE_TIME) * 1000)}</u></b>"

    if imdb:
        cap = IMDB_TEMPLATE.format(
            query=query_by,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            chat=message.chat.title,
            **locals()
        )
    else:
        cap = query_by  # f"Here Is What I Found For Your Query {search}"

    if imdb and imdb.get('poster'):
        try:
            d_msg = await message.reply_photo(photo=imdb.get('poster'), caption=cap,
                                              reply_markup=InlineKeyboardMarkup(btn))

            # if AUTO_DELETE:
            #     await asyncio.sleep(int(DELETE_TIME))
            #     await message.delete()
            #     await d_msg.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            d_msg = await message.reply_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn))

            # if AUTO_DELETE:
            #     await asyncio.sleep(int(DELETE_TIME))
            #     await message.delete()
            #     await d_msg.delete()
        except Exception as e:
            logger.exception(e)
            # await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
            d_msg = await client.send_photo(
                chat_id=msg.chat.id,
                photo=random.choice(PICS),
                caption=cap,
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode="html",
                reply_to_message_id=msg.message_id)

            # if AUTO_DELETE:
            #     await asyncio.sleep(int(DELETE_TIME))
            #     await message.delete()
            #     await d_msg.delete()
    else:
        # await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
        d_msg = await client.send_photo(
            chat_id=msg.chat.id,
            photo=random.choice(PICS),
            caption=cap,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode="html",
            reply_to_message_id=msg.message_id)
    if spoll:
        await msg.message.delete()

    if AUTO_DELETE:
        await asyncio.sleep(int(DELETE_TIME))
        await message.delete()
        await d_msg.delete()


async def advantage_spell_chok(client, msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        Send_message = await client.send_video(
            chat_id=msg.chat.id,
            video="https://telegra.ph/file/1fbdc1703b58c5c0ed242.mp4",
            caption=f"Couldn't Find This Series.Please Try Again Or Search On Our "
                    f"<b><a href='https://t.me/M76Links'>Channel</a></b>. \n\n"
                    f"ഈ സീരീസ്ന്റ് ഒറിജിനൽ പേര് ഗൂഗിളിൽ പോയി കണ്ടെത്തി അതുപോലെ ഇവിടെ കൊടുക്കുക 🥺",
            parse_mode="html",
            reply_to_message_id=msg.message_id
        )
        await asyncio.sleep(15)  # in seconds
        await Send_message.delete()
        await msg.delete()
        # k = await msg.reply("I couldn't find any movie in that name.")
        # await asyncio.sleep(8)
        # await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        for mov in gs_parsed:
            imdb_s = await get_poster(mov.strip(), bulk=True)  # searching each keyword in imdb
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        Send_message = await client.send_video(
            chat_id=msg.chat.id,
            video="https://telegra.ph/file/1fbdc1703b58c5c0ed242.mp4",
            caption=f"Couldn't Find This Series.Please Try Again Or Search On Our "
                    f"<b><a href='https://t.me/TvSeriesLand4U_Updates'>Channel</a></b>. \n\n"
                    f"ഈ സീരീസ്ന്റ് ഒറിജിനൽ പേര് ഗൂഗിളിൽ പോയി കണ്ടെത്തി അതുപോലെ ഇവിടെ കൊടുക്കുക 🥺",
            parse_mode="html",
            reply_to_message_id=msg.message_id
        )
        await asyncio.sleep(15)  # in seconds
        await Send_message.delete()
        await msg.delete()
        # k = await msg.reply("I Couldn't Find Anything Related To That. Check Your Spelling")
        # await asyncio.sleep(8)
        # await k.delete()
        return
    SPELL_CHECK[msg.message_id] = movielist
    i = 1
    pre_len = {}
    btn = []
    # movielist.sort(key=len)
    for k, movie in enumerate(movielist):
        text = movie.strip()  # args[2]
        same = False
        if (i % 2) == 0:
            if len(text) > 10 or len(str(pre_len["text_len"])) > 10:
                same = False
            else:
                same = True
        else:
            pre_len["text_len"] = len(text)
            same = False

        i += 1

        btn.append([text, f"spolling#{user}#{k}", same])

    btn.append(["❌ Close", f'spolling#{user}#close_spellcheck', False])
    btn = build_keyboard(btn)

    btn.insert(0, [
        InlineKeyboardButton("📺 Wᴇʙ Sᴇʀɪᴇs", url="https://t.me/TvSeriesLand4U")
    ])

    btn.insert(0, [
        InlineKeyboardButton("🗞️ Updates", url="https://t.me/M76Links"),
        InlineKeyboardButton("🎬 ɴᴇᴡ ᴍᴏᴠɪᴇs", url="https://t.me/onlymovie76")
    ])

    # btn = [[
    #                InlineKeyboardButton(
    #                    text=movie.strip(),
    #                    callback_data=f"spolling#{user}#{k}",
    #                )
    #            ] for k, movie in enumerate(movielist)]
    # btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    # btn.insert(0, [
    #     InlineKeyboardButton("🗞️ Updates", url="https://t.me/M76Links"),
    #     InlineKeyboardButton("🎬 ɴᴇᴡ ᴍᴏᴠɪᴇs", url="https://t.me/onlymovie76")
    # ])
    await msg.reply("I Couldn't Find Anything Related To That\nDid You Mean Any One Of These 👇🏻?",
                    reply_markup=InlineKeyboardMarkup(btn))


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(InlineKeyboardButton(btn[0], callback_data=btn[1]))
        else:
            keyb.append([InlineKeyboardButton(btn[0], callback_data=btn[1])])

    return keyb
