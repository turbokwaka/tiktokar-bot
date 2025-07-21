import re
import subprocess
import uuid

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def download_video(url: str) -> str:
    output_file = f"{uuid.uuid4()}.mp4"

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()

    match = re.search(r'src="(https?://[^"]+\.m3u8)"', html)
    if not match:
        print("No m3u8 URL found")
        return None

    m3u8_url = match.group(1).replace("&amp;", "&")
    print(f"Found m3u8: {m3u8_url}")
    print(f"Downloading to {output_file}...")

    cmd = [
        "ffmpeg", "-i", m3u8_url,
        "-c", "copy", "-bsf:a", "aac_adtstoasc",
        "-loglevel", "error",
        output_file
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Saved: {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None

def download_photo(url: str) -> str:
    output_file = f"{uuid.uuid4()}.jpg"

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()

    match = re.search(r'src="(https?://[^"]+\.jpg)"', html)
    if not match:
        print("No JPG URL found")
        return None

    img_url = match.group(1)
    print(f"Found image: {img_url}")
    response = requests.get(img_url)
    if response.status_code != 200:
        print("Image download failed")
        return None

    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"Saved: {output_file}")
    return output_file

def fuck_pinterest(url: str) -> str:
    # resolve pin.it redirects
    if url.startswith("https://pin.it/"):
        r = requests.get(url, allow_redirects=True)
        url = r.url

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()

    if "<video" in html:
        return download_video(url)
    else:
        return download_photo(url)
