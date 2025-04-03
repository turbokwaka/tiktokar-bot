import uuid
import requests
import json
import os
from typing import Optional
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

token = os.environ.get("TOKEN")
url = os.environ.get("URL")
admin_chat_id = os.environ.get("ADMIN_CHAT_ID")

if not token or not url:
    raise ValueError("TOKEN and URL must be set in the environment!")

async def receive_content_url(user_input):
    payload = { "url": user_input }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers).json()
        print(json.dumps(response, indent=4))

        if response.get("status") in ("tunnel", "redirect"):
            return response.get("url"), "video"
        else:
            return response, "images"
    except Exception as e:
        await send_error_log(user_input, update=None)
        return None, None


def download_video(content_url):
    video_filename = f"{uuid.uuid4()}.mp4"
    try:
        video_response = requests.get(content_url, stream=True)
        if video_response.status_code != 200:
            return None

        with open(video_filename, "wb") as file:
            for chunk in video_response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                file.write(chunk)

        return video_filename
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None


def download_photos(response_data):
    photo_filenames = []

    try:
        if response_data.get("status") != "picker" or "picker" not in response_data:
            print("Invalid JSON format for images")
            return []

        for item in response_data["picker"]:
            if item.get("type") == "photo":
                photo_url = item.get("url")
                if photo_url:
                    filename = f"{uuid.uuid4()}.jpeg"
                    resp = requests.get(photo_url, stream=True)
                    if resp.status_code == 200:
                        with open(filename, "wb") as file:
                            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                                file.write(chunk)
                        photo_filenames.append(filename)
                    else:
                        print(f"Failed to download {photo_url}")
    except Exception as e:
        print(f"Error downloading photos: {str(e)}")

    return photo_filenames

async def send_error_log(info, update, context):
    """Send error information to admin chat with user details"""
    try:
        # Get user information
        user = update.effective_user
        user_identifier = user.username or user.first_name or "Unknown user"

        # Get user's input text if available
        user_input = update.message.text if update.message and update.message.text else "No text input"

        # Format the log message
        log_message = f"User: {user_identifier}\n\nInput: {user_input}\n\nAPI Response: {info}"

        # Send to admin only using context.bot
        await context.bot.send_message(chat_id=admin_chat_id, text=log_message)
    except Exception as e:
        logger.error(f"Failed to send error log: {e}")


async def handle_any_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response_data, content_type = await receive_content_url(update.message.text)

    if not response_data:
        await update.message.reply_text("Error processing the URL.")
        await send_error_log(response_data, update, context)
        return

    if content_type == "video":
        video_filename = download_video(response_data)
        if video_filename:
            with open(video_filename, "rb") as file:
                await update.message.reply_video(video=file)
            os.remove(video_filename)
        else:
            await update.message.reply_text("Failed to download the video.")
            await send_error_log(response_data, update)
    elif content_type == "images":
        photo_filenames = download_photos(response_data)
        if photo_filenames:
            for filename in photo_filenames:
                with open(filename, "rb") as file:
                    await update.message.reply_photo(photo=file)
                os.remove(filename)
        else:
            await update.message.reply_text("Failed to download images.")
            await send_error_log(response_data, update, context)
    else:
        await update.message.reply_text("Unsupported content type.")
        await send_error_log(response_data, update, context)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! Send me a URL to get started.")

app = ApplicationBuilder().token(token).build()

app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_any_text
))

app.add_handler(CommandHandler("start", handle_start))

app.run_polling()
