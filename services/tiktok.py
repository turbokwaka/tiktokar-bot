import re
import json
import uuid

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def خذ_هذا_الرابط_الغبي_وابحث_فيه_عن_شيء_يبدو_وكأنه_مقطع_فيديو_أو_صورة_غبية(url):
    is_short_link = re.match(r'^https://vm\.tiktok\.com/[A-Za-z0-9]+/?$', url)
    video_id = None

    if is_short_link:
        response = requests.get(url, allow_redirects=True)
        final_url = response.url

        # Витягуємо ID з фінального URL
        match = re.search(r'/(video|photo)/(\d+)', final_url)
        if match:
            video_id = match.group(2)
        else:
            print("❌ Не вдалося знайти ID у фінальному URL")

    print("🎥 Video ID:", video_id)

    options = Options()
    options.add_argument("--headless")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)

    video_page_url = f"https://www.tiktok.com/@i/video/{video_id}"
    if video_id:
        driver.get(video_page_url)

    html = driver.page_source

    match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', html,
                      re.DOTALL)

    if match:
        json_str = match.group(1)
        data = json.loads(json_str)

        details = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]

        image_post = details.get("itemInfo").get("itemStruct").get("imagePost")

        if image_post:
            print("There is images!!!")
            for im in image_post["images"]:
                im_url = im["imageURL"]["urlList"][0]
                print(im_url)

                session = requests.Session()
                response = session.get(im_url)

                response.raise_for_status()

                file_name = str(uuid.uuid4())
                with open(f"{file_name}.jpeg", "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
        else:
            video_url = details["itemInfo"]["itemStruct"]["video"]["playAddr"]

            selenium_cookies = driver.get_cookies()
            driver.quit()

            session = requests.Session()

            headers = {
                "Referer": video_page_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            }
            session.headers.update(headers)

            # Додаємо cookies, отримані з Selenium, до сесії requests
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

            try:
                response = session.get(video_url, stream=True, timeout=30)

                response.raise_for_status()

                file_name = str(uuid.uuid4())
                with open(f"{file_name}.mp4", "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            except requests.exceptions.RequestException as e:
                print(f"❌ Помилка під час завантаження відео: {e}")
    else:
        driver.quit()
        print("❌ Не вдалося знайти потрібний скрипт на сторінці.")


خذ_هذا_الرابط_الغبي_وابحث_فيه_عن_شيء_يبدو_وكأنه_مقطع_فيديو_أو_صورة_غبية("https://vm.tiktok.com/ZMS4uoRet/")