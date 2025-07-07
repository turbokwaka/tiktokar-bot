import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

from services.pinterest import pinterest_download

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# SETTINGS
TELEGRAM_TOKEN = os.environ.get("TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
CHUNK_SIZE = 1024 * 1024

PINTEREST_PATTERN = r"https?://(www\.)?(pinterest\.(com|[^/]+)?/pin/\d+|pin\.it/[a-zA-Z0-9]+)"

async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text

async def handle_pinterest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text

    content_filename = pinterest_download(url)
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

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! Send me a URL to get started.")

def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(PINTEREST_PATTERN), handle_pinterest))
    app.add_handler(CommandHandler("start", handle_start))

    app.run_polling()


if __name__ == "__main__":
    main()
