import logging
import os

import dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

from services.pinterest import fuck_pinterest
from services.tiktok import fuck_tiktok
from services.pornhub import fuck_pornhub
from services.youtube import fuck_youtube
from services.random_kitty import get_kitty

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# SETTINGS
TELEGRAM_TOKEN = dotenv.dotenv_values(".env").get("TELEGRAM_TOKEN")
CHUNK_SIZE = 1024 * 1024

PINTEREST_PATTERN = r"https?://(www\.)?(pinterest\.(com|[^/]+)?/pin/\d+|pin\.it/[a-zA-Z0-9]+)"
TIKTOK_PATTERN = r"https?://vm\.tiktok\.com/[A-Za-z0-9]+/?"
PORNHUB_PATTERN = r"^https?://(?:www\.)?pornhub\.com/view_video\.php\?viewkey=[A-Za-z0-9]+$"
YTMUSIC_PATTERN = r"https?://(?:www\.)?music\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}(?:&si=[A-Za-z0-9_-]+)?"


async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text

    content = fuck_tiktok(url)
    if isinstance(content, list):
        for i in content:
            await update.effective_chat.send_photo(i)
            os.remove(i)
        return
    elif isinstance(content, str):
        if content.endswith(".mp4"):
            await update.effective_chat.send_video(content)
            os.remove(content)
            return

async def handle_pinterest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text

    content_filename = fuck_pinterest(url)
    if not content_filename:
        await update.effective_chat.send_message("Щось пішло не так. Перевір посилання.")
        return
    elif content_filename.endswith(".mp4"):
        await update.effective_chat.send_video(content_filename)
        os.remove(content_filename)
        return
    elif content_filename.endswith(".jpg"):
        await update.effective_chat.send_photo(content_filename)
        os.remove(content_filename)
        return

async def handle_pornhub(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text

    loading_msg = await update.effective_chat.send_message("Завантаження може зайняти багато часу...")
    content_filename = fuck_pornhub(url)
    if not content_filename:
        await update.effective_chat.send_message("Щось пішло не так. Перевір посилання.")
        return
    elif content_filename.endswith(".mp4"):
        await loading_msg.delete()
        await update.effective_chat.send_video(content_filename)
        await update.effective_chat.send_message("🍷")

        os.remove(content_filename)
        return

async def handle_ytmusic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text

    content_filename = fuck_youtube(url)
    if not content_filename or content_filename == "":
        await update.effective_chat.send_message("Щось пішло не так. Перевір посилання.")
    elif content_filename.endswith(".mp3"):
        await update.effective_chat.send_document(content_filename)
        await update.effective_chat.send_message("🥃")
        os.remove(content_filename)
        return

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message("Привіт! Скидай мені шось, шо я знаю, або іди нахуй.")
    await update.effective_chat.send_message("Кстаті, ось тобі кітик 😌")
    await update.effective_chat.send_animation(animation=get_kitty())

async def pizdec_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message("Щось пішло не так. Ось тобі кітик ☺️")
    await update.effective_chat.send_animation(animation=get_kitty())

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(PINTEREST_PATTERN), handle_pinterest))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(TIKTOK_PATTERN), handle_tiktok))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(PORNHUB_PATTERN), handle_pornhub))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(YTMUSIC_PATTERN), handle_ytmusic))
    app.add_handler(CommandHandler("start", handle_start))

    app.run_polling()


if __name__ == "__main__":
    main()
