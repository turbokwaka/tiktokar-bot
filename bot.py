import logging
import os
import re
import uuid

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
from yt_dlp import YoutubeDL

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# SETTINGS
TELEGRAM_TOKEN = os.environ.get("TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
CHUNK_SIZE = 1024 * 1024

# CONSTANTS
TIKTOK_VIDEO, TIKTOK_PHOTOS, YT_VIDEO, YT_MUSIC, INST_REELS, SYBAU = (
    "TIKTOK_VIDEO",
    "TIKTOK_PHOTOS",
    "YT_VIDEO",
    "YT_MUSIC",
    "INST_REELS",
    "SYBAU"
)

# REGEX DICT
REGEX_PATTERNS = {
    TIKTOK_VIDEO: [
        re.compile(r'https?://vm\.tiktok\.com/\w+/?'),
    ],
    TIKTOK_PHOTOS: [
        re.compile(r'https?://(www\.)?tiktok\.com/@[\w\.-]+/photo/\d+'),
    ],
    YT_VIDEO: [
        re.compile(r'https?://(www\.)?youtube\.com/watch\?v=[\w-]+'),
        re.compile(r'https?://youtu\.be/[\w-]+'),
    ],
    YT_MUSIC: [
        re.compile(r'https?://music\.youtube\.com/watch\?v=[\w-]+'),
    ],
    INST_REELS: [
        re.compile(r'https?://(www\.)?instagram\.com/reel/[\w-]+'),
        re.compile(r'https:\/\/www\.instagram\.com\/[^\/]+\/reel\/[A-Za-z0-9_-]+\/?'),
    ],
}

async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    content_type = get_tiktok_content_type(url)

    if content_type is TIKTOK_VIDEO:
        file_name = str(uuid.uuid4())
        options = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{file_name}.%(ext)s',
            'merge_output_format': 'mp4'
        }
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        with open(f"{file_name}.mp4", "rb") as file:
            await update.message.reply_video(video=file)
    if content_type is TIKTOK_PHOTOS:
        with YoutubeDL() as ydl:
            ydl.download([url])

def get_tiktok_content_type(short_url):
    try:
        response = requests.get(short_url, allow_redirects=True, timeout=5)
        final_url = response.url
        logger.info(f"Redirected URL: {final_url}")
        if '/video/' in final_url:
            return TIKTOK_VIDEO
        elif '/photo/' in final_url:
            return TIKTOK_PHOTOS
        else:
            return SYBAU
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {short_url}: {e}")
        return SYBAU

def check_content_type(user_input: str) -> str:
    for pattern_type, patterns in REGEX_PATTERNS.items():
        for pattern in patterns:
            if pattern.match(user_input):
                logger.info(f"Matched pattern {pattern.pattern} for type {pattern_type}")
                if pattern_type == TIKTOK_VIDEO and 'vm.tiktok.com' in user_input:
                    return get_tiktok_content_type(user_input)
                return pattern_type
    return SYBAU

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text

    content_type = check_content_type(user_input)
    if content_type == SYBAU:
        await update.effective_chat.send_message("HEEELLL NAAWWW")
    if content_type == TIKTOK_VIDEO:
        await update.effective_chat.send_message("TIKTOK_VIDEO")
    if content_type == TIKTOK_PHOTOS:
        await update.effective_chat.send_message("TIKTOK_PHOTOS")
    if content_type == YT_VIDEO:
        await update.effective_chat.send_message("YT_VIDEO")
    if content_type == YT_MUSIC:
        await update.effective_chat.send_message("YT_MUSIC")
    if content_type == INST_REELS:
        await update.effective_chat.send_message("INST_REELS")

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! Send me a URL to get started.")

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(REGEX_PATTERNS[TIKTOK_VIDEO][0]), handle_tiktok))
    app.add_handler(CommandHandler("start", handle_start))

    app.run_polling()


if __name__ == "__main__":
    main()
