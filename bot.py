from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import requests
import os
import uuid

# cobalt default port is 9000
# enable port forwarding to your desired port
url = ""
token = ""

def receive_url(user_input):
    payload = {"url": user_input}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers).json()
        return response.get("url", None)
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


async def handle_any_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video_url = receive_url(update.message.text)

    if not video_url:
        await update.message.reply_text("⚠️ Failed to fetch video URL.")
        return

    video_filename = f"{uuid.uuid4()}.mp4"

    try:
        video_response = requests.get(video_url, stream=True)
        if video_response.status_code != 200:
            await update.message.reply_text("⚠️ Failed to download video.")
            return

        with open(video_filename, "wb") as file:
            for chunk in video_response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                file.write(chunk)

        with open(video_filename, "rb") as file:
            await update.message.reply_video(video=file)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")
    finally:
        if os.path.exists(video_filename):
            os.remove(video_filename)


app = ApplicationBuilder().token(token).build()

app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_any_text
))

app.run_polling()
