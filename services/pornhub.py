import os
import re
import uuid
import subprocess
import logging

from services.create_driver import hell_yeah
from services.tunnel_file import java_squirt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fuck_pornhub(url: str):
    m3u8_url = None

    driver = hell_yeah()
    driver.get(url)
    html = driver.page_source

    match = re.search(r'"videoUrl":"(https:\\/\\/[^"]+?\.m3u8[^"]*)"', html)
    if match:
        m3u8_url = match.group(1).replace("\\/", "/")
        logger.info("🔗 m3u8 URL: %s", m3u8_url)
    else:
        logger.error("❌ Не знайдено URL")
        driver.quit()
        return None

    cookies = driver.get_cookies()
    cookie_string = '; '.join(f"{c['name']}={c['value']}" for c in cookies)
    driver.quit()

    output_file = f"{uuid.uuid4()}.mp4"
    referer = "https://www.pornhub.com"
    user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36")

    cmd = [
        "ffmpeg",
        "-user_agent", user_agent,
        "-headers", f"Referer: {referer}\r\nCookie: {cookie_string}",
        "-i", m3u8_url,
        "-c", "copy",
        "-loglevel", "error",
        output_file
    ]

    logger.info("📥 Starting download...")
    try:
        subprocess.run(cmd, check=True)
        logger.info("✅ Download finished: %s", output_file)
    except subprocess.CalledProcessError as e:
        logger.error("❌ FFmpeg error: %s", e)
        if os.path.exists(output_file):
            os.remove(output_file)
        return None

    return java_squirt(output_file)