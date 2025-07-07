# import subprocess
# import uuid
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import re
# import requests
#
# url = "https://www.pornhub.com/view_video.php?viewkey=649fdb62152d6"
# m3u8_url = None
# options = Options()
# options.add_argument("--headless")
# driver = webdriver.Chrome(options=options)
# driver.get(url)
#
# html = driver.page_source
# with open("ph_html.html", "w", encoding="utf-8") as f:
#     f.write(html)
#
# match = re.search(r'"videoUrl":"(https:\\/\\/[^"]+\.mp4\\/master\.m3u8[^"]*)","quality":"1080"', html)
# if not match:
#     match = re.search(r'"videoUrl":"(https:\\/\\/[^"]+\.mp4\\/master\.m3u8[^"]*)","quality":"720"', html)
# if not match:
#     match = re.search(r'"videoUrl":"(https:\\/\\/[^"]+\.mp4\\/master\.m3u8[^"]*)","quality":"360"', html)
#
# if match:
#     m3u8_url = match.group(1).replace("\\/", "/")  # Розекранувати
#     print("🔗 m3u8 URL:", m3u8_url)
# else:
#     print("❌ Не знайдено URL")
#
# driver.quit()
#
# import subprocess
# from tqdm import tqdm
#
# output_file = str(uuid.uuid4()) + ".mp4"
# referer = "https://www.pornhub.com"
#
# # Отримуємо тривалість відео (в секундах) через ffprobe
# def get_video_duration(url):
#     cmd = [
#         "ffprobe",
#         "-headers", f"Referer: {referer}",
#         "-i", url,
#         "-show_entries", "format=duration",
#         "-v", "quiet",
#         "-of", "csv=p=0"
#     ]
#     result = subprocess.run(cmd, capture_output=True, text=True)
#     try:
#         return float(result.stdout.strip())
#     except:
#         return None
#
# duration = get_video_duration(m3u8_url)
# if not duration:
#     print("❌ Не вдалося визначити тривалість відео.")
#     exit()
#
# # Запускаємо ffmpeg з прогрес-індикатором
# cmd = [
#     "ffmpeg",
#     "-headers", f"Referer: {referer}",
#     "-i", m3u8_url,
#     "-c", "copy",
#     "-progress", "pipe:1",
#     "-nostats",
#     "-loglevel", "error",
#     output_file
# ]
#
# print(f"🚀 Завантаження відео...")
#
# with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc:
#     pbar = tqdm(total=duration, unit="s", bar_format="{l_bar}{bar}| {n:.0f}/{total:.0f} сек")
#     for line in proc.stdout:
#         if "out_time_us=" in line:
#             out_time_us = int(line.strip().split("=")[1])
#             seconds = out_time_us / 1_000_000
#             pbar.n = seconds
#             pbar.refresh()
#         elif "progress=end" in line:
#             break
#
#     proc.wait()
#     pbar.n = duration
#     pbar.refresh()
#     pbar.close()
#
# print("✅ Завантаження завершено!")
#
#

import subprocess
import uuid

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import requests

url = "https://www.pornhub.com/view_video.php?viewkey=649fdb62152d6"
m3u8_url = None
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(url)

html = driver.page_source
with open("ph_html.html", "w", encoding="utf-8") as f:
    f.write(html)

match = re.search(r'"videoUrl":"(https:\\/\\/[^"]+\.mp4\\/master\.m3u8[^"]*)","quality":"1080"', html)
if not match:
    match = re.search(r'"videoUrl":"(https:\\/\\/[^"]+\.mp4\\/master\.m3u8[^"]*)","quality":"720"', html)
if not match:
    match = re.search(r'"videoUrl":"(https:\\/\\/[^"]+\.mp4\\/master\.m3u8[^"]*)","quality":"360"', html)

if match:
    m3u8_url = match.group(1).replace("\\/", "/")
    print("🔗 m3u8 URL:", m3u8_url)
else:
    print("❌ Не знайдено URL")
    driver.quit()
    exit()

driver.quit()

output_file = str(uuid.uuid4()) + ".mp4"
referer = "https://www.pornhub.com"

cmd = [
    "ffmpeg",
    "-headers", f"Referer: {referer}",
    "-i", m3u8_url,
    "-c", "copy",
    "-loglevel", "error",
    output_file
]

subprocess.run(cmd)
print("✅ Завантаження завершено:", output_file)

