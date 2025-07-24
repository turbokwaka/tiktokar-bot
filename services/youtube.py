import re
import uuid
import logging
from time import sleep

from yt_dlp import YoutubeDL
from services.create_driver import hell_yeah
from services.utils import fuck_around

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_music(url: str) -> str:
    title_pattern = r'<yt-formatted-string[^>]*?class="title style-scope ytmusic-player-bar"[^>]*?>([^<]+)</yt-formatted-string>'
    author_pattern = r'<yt-formatted-string[^>]*class="byline style-scope ytmusic-player-queue-item"[^>]*>([^<]+)</yt-formatted-string>'

    title = None
    author = None
    final_name = None

    driver = hell_yeah()

    logger.info("Retrieving page source... help")
    driver.get(url)
    sleep(5)
    html = driver.page_source
    driver.quit()

    title = fuck_around(html, title_pattern)
    author = fuck_around(html, author_pattern)

    if title != "":
        final_name = f"{title} - {author}"
    else:
        final_name = f"FUCKIN UNTITLED - {author}"

    final_name = re.sub(r'[^0-9A-Za-z._-]', '-', final_name)


    kurwa_options = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'outtmpl': f"{final_name}.%(ext)s",
    }

    try:
        logging.info(f"Downloading from yt-music: {url}")
        with YoutubeDL(kurwa_options) as ydl:
            ydl.download([url])
        return f"{final_name}.mp3"
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        return ""

def fuck_youtube(url: str) -> str:
    return download_music(url)