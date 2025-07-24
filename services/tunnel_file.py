import logging
import os
import time

from selenium.webdriver.common.by import By

from services.create_driver import hell_yeah

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def java_squirt(file_path: str, keep_alive_minutes: int = 30):
    driver = hell_yeah()

    try:
        driver.get('https://file.pizza/')

        upload_input = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')

        abs_path = os.path.abspath(file_path)
        upload_input.send_keys(abs_path)

        time.sleep(3)

        start_button = driver.find_element(By.ID, "start-button")
        start_button.click()

        time.sleep(3)

        share_input = driver.find_element(By.ID, 'copyable-input-short-url')
        link = share_input.get_attribute('value')
        logger.info(f"P2P‑link:\n{link}")
        logger.info(f"Lives {keep_alive_minutes} min.")

        time.sleep(keep_alive_minutes * 60)
    except Exception as e:
        logger.error(f"Error while tunneling: {e}")
    finally:
        driver.quit()
        logger.info("FUCK")