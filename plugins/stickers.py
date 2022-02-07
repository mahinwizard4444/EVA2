import os, glob
from os import error
import logging
import pyrogram
import time
import math

from info import *
from decouple import config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import User, Message, Sticker, Document


@Client.on_message(filters.command(["ping"]))
async def ping(bot, message):
    start_t = time.time()
    rm = await message.reply_text("Checking")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Pong!\n{time_taken_s:.3f} ms")
    await message.delete()


@Client.on_message(filters.private & filters.command(["getsticker"]))
async def getstickerasfile(bot, message):
    tx = await message.reply_text("Checking Sticker")
    await tx.edit("Validating sticker..")
    if message.reply_to_message.sticker is False:
        await tx.edit("Not a Sticker File!!")
    else:
        if message.reply_to_message is None:
            tx = await tx.edit("Reply to a Sticker File!")
        else:
            if message.reply_to_message.sticker.is_animated:
                try:
                    tx = await message.reply_text("Downloading...")
                    file_path = TMP_DOWNLOAD_DIRECTORY + f"{message.chat.id}.tgs"
                    await message.reply_to_message.download(file_path)
                    await tx.edit("Downloaded")
                    #   zip_path= ZipFile.write("")
                    await tx.edit("Uploading...")
                    start = time.time()
                    powered_by = "<b>[<a href='https://t.me/TvSeriesLand4U'>©𝕄𝕚𝕝𝕝𝕚𝕖</a>]</b>"
                    await message.reply_document(
                        document=file_path,
                        caption=f"💫 ℙ𝕠𝕨𝕖𝕣𝕖𝕕 𝔹𝕪 : {powered_by}",
                        parse_mode="html")
                    await tx.delete()
                    os.remove(file_path)
                #   os.remove(zip_path)
                except Exception as error:
                    print(error)

            elif message.reply_to_message.sticker.is_animated is False:
                try:
                    tx = await message.reply_text("Downloading...")
                    file_path = TMP_DOWNLOAD_DIRECTORY + f"{message.chat.id}.png"
                    await message.reply_to_message.download(file_path)
                    await tx.edit("Downloaded")
                    await tx.edit("Uploading...")
                    start = time.time()
                    powered_by = "<b>[<a href='https://t.me/TvSeriesLand4U'>𝕄𝕚𝕝𝕝𝕚𝕖</a>]</b>"
                    await message.reply_document(
                        document=file_path,
                        caption=f"💫 ℙ𝕠𝕨𝕖𝕣𝕖𝕕 𝔹𝕪 : {powered_by}",
                        parse_mode="html")
                    await tx.delete()
                    os.remove(file_path)
                except Exception as error:
                    print(error)


@Client.on_message(filters.private & filters.command(["clearcache"]))
async def clearcache(bot, message):
    # Found some Files showing error while Uploading, So a method to Remove it !!  
    txt = await message.reply_text("Checking Cache")
    await txt.edit("Clearing cache")
    dir = TMP_DOWNLOAD_DIRECTORY
    filelist = glob.glob(os.path.join(dir, "*"))
    for f in filelist:
        i = 1
        os.remove(f)
        i = i + 1
    await txt.edit("Cleared " + str(i) + "File")
    await txt.delete()


@Client.on_message(filters.command(["stickerid"]))
async def stickerid(bot, message):
    if message.reply_to_message.sticker:
        await message.reply(
            f"**Sticker ID is**  \n `{message.reply_to_message.sticker.file_id}` \n \n ** Unique ID is ** \n\n`{message.reply_to_message.sticker.file_unique_id}`",
            quote=True)
    else:
        await message.reply("Oops !! Not a sticker file")


@Client.on_message(filters.private & filters.command(["findsticker"]))
async def findsticker(bot, message):
    try:
        if message.reply_to_message:
            txt = await message.reply_text("Validating Sticker ID")
            stickerid = str(message.reply_to_message.text)
            chat_id = str(message.chat.id)
            await txt.delete()
            await bot.send_sticker(chat_id, f"{stickerid}")
        else:
            await message.reply_text("Please Reply To A ID To Get Its STICKER.")
    except Exception as error:
        txt = await message.reply_text("Not A Valid File ID")

__help__ = """
 - /getsticker: Generate Your Sticker As Image (.png). 
 - /clearcache: Clear Cache Files.
 - /stickerid: Get Your Sticker Id.
 - /findsticker: Find Your Sticker By Using Sticker Id.
 
 * Send Sticker & Reply With Command /getsticker For Getting Image.
 * Send Sticker & Reply With Command /stickerid For Getting Sticker Id.
 * Send Sticker Id & Reply With Command /findsticker For Getting Sticker.
"""

__mod_name__ = "Sticker"
