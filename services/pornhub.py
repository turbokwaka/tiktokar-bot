import os
import re
import uuid
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def fuck_pornhub(url: str):
    m3u8_url = None
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    html = driver.page_source

    match = re.search(r'"videoUrl":"(https:\\/\\/[^"]+?\.m3u8[^"]*)"', html)
    if match:
        m3u8_url = match.group(1).replace("\\/", "/")
        print("🔗 m3u8 URL:", m3u8_url)
    else:
        print("❌ Не знайдено URL")
        driver.quit()
        return None

    cookies = driver.get_cookies()
    cookie_string = '; '.join([f"{c['name']}={c['value']}" for c in cookies])

    driver.quit()

    output_file = f"{uuid.uuid4()}.mp4"
    referer = "https://www.pornhub.com"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

    cmd = [
        "ffmpeg",
        "-user_agent", user_agent,
        "-headers", f"Referer: {referer}\r\nCookie: {cookie_string}",
        "-i", m3u8_url,
        "-c", "copy",
        "-loglevel", "error",
        output_file
    ]

    print("📥 Starting download...")
    try:
        subprocess.run(cmd, check=True)
        print("✅ Завантаження завершено:", output_file)
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e}")
        os.remove(output_file)
        return None

    return output_file
