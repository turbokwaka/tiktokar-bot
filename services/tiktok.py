import re
import json
import uuid
import logging
from telnetlib import EC
from time import sleep

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from services.create_driver import hell_yeah

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fuck_tiktok(url):
    logger.info(f"Start processing URL: {url}")
    is_short_link = re.match(r'^https://vm\.tiktok\.com/[A-Za-z0-9]+/?$', url)
    video_id = None

    if is_short_link:
        logger.info("Resolving short link...")
        response = requests.get(url, allow_redirects=True)
        final_url = response.url
        logger.info(f"Resolved URL: {final_url}")

        match = re.search(r'/(video|photo)/(\d+)', final_url)
        if match:
            video_id = match.group(2)
            logger.info(f"Found ID: {video_id}")
        else:
            logger.info("No ID found in redirect URL")
            return None

    logger.info(f"Video ID: {video_id}")

    driver = hell_yeah()

    video_page_url = f"https://www.tiktok.com/@i/video/{video_id}"
    logger.info(f"Loading page: {video_page_url}")
    driver.get(video_page_url)
    logger.info("Page source retrieved")

    try:
        script_tag = driver.find_element(By.ID, "__UNIVERSAL_DATA_FOR_REHYDRATION__")
        json_data = script_tag.get_attribute("innerHTML")
        data = json.loads(json_data)
    except Exception as e:
        logger.error(f"Failed to extract JSON data from script tag: {e}")
        driver.quit()
        return None

    details = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]
    item = details.get("itemInfo", {}).get("itemStruct", {})

    image_post = item.get("imagePost")
    if image_post:
        logger.info("Image post detected")
        images = []
        for im in image_post["images"]:
            im_url = im["imageURL"]["urlList"][0]
            logger.info(f"Downloading image: {im_url}")
            session = requests.Session()
            response = session.get(im_url)
            response.raise_for_status()
            file_name = f"{uuid.uuid4()}.jpeg"
            with open(file_name, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Saved image: {file_name}")
            images.append(file_name)
        driver.quit()
        return images

    video_url = item.get("video", {}).get("playAddr")
    if not video_url:
        driver.quit()
        logger.info("No video URL found")
        return None

    logger.info(f"Video URL: {video_url}")
    selenium_cookies = driver.get_cookies()
    driver.quit()

    session = requests.Session()
    session.headers.update({
        "Referer": video_page_url,
        "User-Agent": "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    })
    for cookie in selenium_cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))

    try:
        logger.info("Starting video download...")
        response = session.get(video_url, stream=True, timeout=30)
        response.raise_for_status()
        file_name = f"{uuid.uuid4()}.mp4"
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Saved video: {file_name}")
        return file_name
    except requests.exceptions.RequestException as e:
        logger.error(f"Download error: {e}")
        return None
