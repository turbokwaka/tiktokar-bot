import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Tuple, Union, Any
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TOKEN")
API_URL = os.environ.get("COBALT_URL")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
CHUNK_SIZE = 1024 * 1024

CONTENT_TYPE_VIDEO = "video"
CONTENT_TYPE_IMAGES = "images"
CONTENT_TYPE_AUDIO = "audio"

STATUS_TUNNEL = "tunnel"
STATUS_REDIRECT = "redirect"
STATUS_PICKER = "picker"

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN must be set in the environment!")


async def process_url(user_input: str) -> Tuple[Optional[Union[str, Dict[str, Any]]], Optional[str]]:
    payload = { "url": user_input }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers).json()
        logger.info(f"API response: {json.dumps(response, indent=4)}")

        if response.get("status") in (STATUS_TUNNEL, STATUS_REDIRECT):
            if response.get("filename").endswith(".mp3"):
                return response.get("url"), CONTENT_TYPE_AUDIO
            else:
                return response.get("url"), CONTENT_TYPE_VIDEO
        else:
            return response, CONTENT_TYPE_IMAGES
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        return None, None


def download_file(url: str, file_extension: str) -> Optional[str]:
    filename = f"{uuid.uuid4()}.{file_extension}"

    try:
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            logger.error(f"Failed to download from {url}: Status {response.status_code}")
            return None

        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                file.write(chunk)
        return filename
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return None


def download_video(content_url: str) -> Optional[str]:
    return download_file(content_url, "mp4")


def download_photos(response_data: Dict[str, Any]) -> List[str]:
    photo_filenames = []

    try:
        if response_data.get("status") != STATUS_PICKER or STATUS_PICKER not in response_data:
            logger.error("Invalid JSON format for images")
            return []

        for item in response_data.get(STATUS_PICKER, []):
            if item.get("type") == "photo" and item.get("url"):
                filename = download_file(item["url"], "jpeg")
                if filename:
                    photo_filenames.append(filename)
    except Exception as e:
        logger.error(f"Error processing photos: {str(e)}")

    return photo_filenames


async def send_error_log(info: Any, update: Optional[Update] = None,
                         context: Optional[ContextTypes.DEFAULT_TYPE] = None) -> None:
    if not ADMIN_CHAT_ID or not context:
        logger.error("Cannot send error log: Missing ADMIN_CHAT_ID or context")
        return

    try:
        user_identifier = "Unknown user"
        chat_id = "No user ID"
        user_input = "No text input"

        if update and update.effective_user:
            user = update.effective_user
            user_identifier = user.username or user.first_name or user_identifier
            chat_id = user.id or chat_id

        if update and update.message and update.message.text:
            user_input = update.message.text

        log_message = f"User: {user_identifier}\n\nChat ID: {chat_id}\n\nInput: {user_input}\n\nAPI Response: {info}"

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=log_message)
    except Exception as e:
        logger.error(f"Failed to send error log: {e}")


async def handle_any_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_identifier = update.effective_user.username or update.effective_user.first_name or "Unknown user"
    user_input = update.message.text
    logger.info(f"Received message - Chat ID: {chat_id} - User: {user_identifier} - Message: {user_input}")

    response_data, content_type = await process_url(update.message.text)

    if not response_data:
        await update.message.reply_text("Не вдалось скачати. Я вже нажалівся Артему.")
        await send_error_log("Failed to process URL", update, context)
        return

    if content_type == CONTENT_TYPE_VIDEO:
        video_filename = download_video(response_data)
        if video_filename:
            with open(video_filename, "rb") as file:
                await update.message.reply_video(video=file)
            os.remove(video_filename)
        else:
            await update.message.reply_text("Не вдалось скачати. Я вже нажалівся Артему.")
            await send_error_log(response_data, update, context)

    elif content_type == CONTENT_TYPE_IMAGES:
        photo_filenames = download_photos(response_data)
        if photo_filenames:
            for filename in photo_filenames:
                with open(filename, "rb") as file:
                    await update.message.reply_photo(photo=file)
                os.remove(filename)
        else:
            await update.message.reply_text("Не вдалось скачати. Я вже нажалівся Артему.")
            await send_error_log(response_data, update, context)

    elif content_type == CONTENT_TYPE_AUDIO:
        audio_filename = download_file(response_data, "mp3")
        with open(audio_filename, "rb") as file:
            await update.message.reply_audio(audio=file)
            await update.message.reply_text("🥃")
            os.remove(audio_filename)

    else:
        await update.message.reply_text("Не вдалось скачати. Я вже нажалівся Артему.")
        await send_error_log(response_data, update, context)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Скинь посилання на тікток і я його скачаю)).")


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.Regex(r'https?://vm\.tiktok\.com/\w+/?') & ~filters.COMMAND, handle_any_text))
    app.add_handler(MessageHandler(filters.Regex(r'https?://music\.youtube\.com/watch\?v=[\w-]+&si=[\w-]+') & ~filters.COMMAND, handle_any_text))
    app.add_handler(CommandHandler("start", handle_start))

    app.run_polling()


if __name__ == "__main__":
    main()
