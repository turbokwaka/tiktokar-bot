import re
import subprocess
import uuid

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def download_video(url: str) -> str:
    output_file = str(uuid.uuid4()) + ".mp4"
    m3u8_url = None

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    html = driver.page_source
    with open("pinterest.html", "w", encoding="utf-8") as f:
        f.write(html)

    driver.quit()


    pattern = r'src="(https?://[^"]+\.m3u8)"'
    match = re.search(pattern, html)

    if match:
        m3u8_url = match.group(1).replace("&amp;", "&")
        print(f"✅ Знайдено m3u8 URL: {m3u8_url}")

        cmd = [
            "ffmpeg",
            "-i", m3u8_url,
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            "-loglevel", "error",
            output_file
        ]

        print("🚀 Починаю завантаження...")
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Завантаження завершено: {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"❌ Помилка під час виконання FFmpeg: {e}")
            return None
    else:
        print("❌ Не вдалося знайти m3u8 URL на сторінці.")
        return None


def download_photo(url: str):
    output_file = str(uuid.uuid4()) + ".jpg"

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    html = driver.page_source

    driver.quit()

    pattern = r'src="(https?://[^"]+\.jpg)"'
    match = re.search(pattern, html)
    if match:
        content_url = match.group(1)
        response = requests.get(content_url)

        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"✅ Фото збережено як {output_file}")
            return output_file
        else:
            print("❌ Не вдалося завантажити зображення")
            return None


def pinterest_download(url: str):
    final_url = None
    if url.startswith("https://pin.it/"):
        response = requests.get(url, allow_redirects=True)
        final_url = response.url
    else:
        final_url = url

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    html = driver.page_source
    content_file_name = None

    if "<video" in html:
        content_file_name = download_video(url)
        return content_file_name
    else:
        content_file_name = download_photo(url)
        return content_file_name
