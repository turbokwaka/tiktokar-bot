import tempfile

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


def hell_yeah():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    profile_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={profile_dir}")
    return Chrome(options=options)