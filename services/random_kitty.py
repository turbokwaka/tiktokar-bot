import uuid

import requests

from services.create_driver import hell_yeah
from services.utils import fuck_around
def get_kitty() -> str:
    find_kitty = "https://randomcatgifs.com"
    kitty_pattern = r'<source\s+src="([^"]+\.mp4)"\s*type="video/mp4">'
    kitty_name = str(uuid.uuid4())

    driver = hell_yeah()
    driver.get(find_kitty)
    html = driver.page_source
    driver.quit()

    kitty_url = fuck_around(html, kitty_pattern)
    return kitty_url


