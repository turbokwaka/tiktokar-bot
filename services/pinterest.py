import re
import subprocess
import uuid
import logging

import requests

from services.create_driver import hell_yeah

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_video(url: str) -> str:
    output_file = f"{uuid.uuid4()}.mp4"

    driver = hell_yeah()
    driver.get(url)
    html = driver.page_source
    driver.quit()

    match = re.search(r'src="(https?://[^"]+\.m3u8)"', html)
    if not match:
        logger.error("No m3u8 URL found")
        return None

    m3u8_url = match.group(1).replace("&amp;", "&")
    logger.info(f"Found m3u8: {m3u8_url}")
    logger.info(f"Downloading to {output_file}...")

    cmd = [
        "ffmpeg", "-i", m3u8_url,
        "-c", "copy", "-bsf:a", "aac_adtstoasc",
        "-loglevel", "error",
        output_file
    ]
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Saved: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e}")
        return None

def download_photo(url: str) -> str:
    output_file = f"{uuid.uuid4()}.jpg"

    driver = hell_yeah()
    driver.get(url)
    html = driver.page_source
    driver.quit()

    match = re.search(r'src="(https?://[^"]+\.jpg)"', html)
    if not match:
        logger.error("No JPG URL found")
        return None

    img_url = match.group(1)
    logger.info(f"Found image: {img_url}")
    response = requests.get(img_url)
    if response.status_code != 200:
        logger.error("Image download failed")
        return None

    with open(output_file, "wb") as f:
        f.write(response.content)
    logger.info(f"Saved: {output_file}")
    return output_file

def fuck_pinterest(url: str) -> str:
    # resolve pin.it redirects
    if url.startswith("https://pin.it/"):
        r = requests.get(url, allow_redirects=True)
        url = r.url

    driver = hell_yeah()
    driver.get(url)
    html = driver.page_source
    driver.quit()

    if "<video" in html:
        return download_video(url)
    else:
        return download_photo(url)
