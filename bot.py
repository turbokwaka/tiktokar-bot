import uuid
import requests
import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

token = os.environ.get("TOKEN")
url = os.environ.get("URL")

if not token or not url:
    raise ValueError("TOKEN and URL must be set in the environment!")

def receive_content_url(user_input):
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
        print(f"Error fetching URL: {e}")
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


async def handle_any_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response_data, content_type = receive_content_url(update.message.text)

    if not response_data:
        await update.message.reply_text("Error processing the URL.")
        return

    if content_type == "video":
        video_filename = download_video(response_data)
        if video_filename:
            with open(video_filename, "rb") as file:
                await update.message.reply_video(video=file)
            os.remove(video_filename)
        else:
            await update.message.reply_text("Failed to download the video.")
    elif content_type == "images":
        photo_filenames = download_photos(response_data)
        if photo_filenames:
            for filename in photo_filenames:
                with open(filename, "rb") as file:
                    await update.message.reply_photo(photo=file)
                os.remove(filename)
        else:
            await update.message.reply_text("Failed to download images.")
    else:
        await update.message.reply_text("Unsupported content type.")


app = ApplicationBuilder().token(token).build()

app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_any_text
))

app.run_polling()
