import random
import time

from loguru import logger
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


class ChromeBrowser:

    def __init__(self, url: str):
        self.b = webdriver.Chrome()
        self.b.implicitly_wait(60)
        self.b.get(url)

    def click(self, key: str, by=By.XPATH, error='raise'):
        try:
            self.get_element(by, key).click()
            time.sleep(random.random())
        except Exception as e:
            if error == 'ignore':
                pass
            else:
                raise e
        return self

    def send(self, key: str, value: str, by=By.XPATH):
        self.get_element(by, key).send_keys(value)
        time.sleep(random.random())
        return self

    def get_element(self, by, key):
        return self.b.find_element(by=by, value=key)

    def enter(self, key: str):
        self.send(key, Keys.ENTER)
        return self

    @staticmethod
    def wait(seconds: int):
        for i in range(seconds):
            logger.info(f'等待 {seconds - i} 秒')
            time.sleep(1)
        return

    def switch_to_next_window(self):
        self.b.switch_to.window(self.b.window_handles[-1])

    def switch_to_last_window(self):
        self.b.close()
        self.b.switch_to.window(self.b.window_handles[0])

    def quit(self):
        self.b.quit()
