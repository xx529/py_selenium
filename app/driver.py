import random
import time

import pandas as pd
from loguru import logger
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.elements import ElementSelector


class ChromeBrowser:

    def __init__(self, selector: ElementSelector):
        self.b = webdriver.Chrome()
        self.selector = selector
        self.b.implicitly_wait(60)

    def open(self, url: str):
        logger.info(f'打开网址：{url}')
        self.b.get(url)
        return self

    def click(self, name: str, error='raise') -> bool:
        logger.info(f'点击`{name}`')
        try:
            self.get_element(name).click()
            time.sleep(random.random())
            return True
        except Exception as e:
            if error == 'ignore':
                return False
            else:
                raise e

    def send(self, name: str, value: str):
        logger.info(f'向`{name}`输入`{value}`')
        self.get_element(name).send_keys(value)
        time.sleep(random.random())
        return self

    def get_element(self, name: str) -> WebElement:
        e = self.selector.get(name)
        return self.b.find_element(e.by, e.key)

    def enter(self, name: str):
        logger.info(f'按回车键`{name}`')
        self.send(name, Keys.ENTER)
        return self

    def get_table(self, name: str) -> pd.DataFrame:
        logger.info(f'获取表格`{name}`')
        e = self.get_element(name)
        data = e.find_elements(by=By.TAG_NAME, value='tr')
        rows = [[x.text for x in d.find_elements(by=By.TAG_NAME, value='td')] for d in data]
        return pd.DataFrame(rows[1:], index=rows[0])

    @staticmethod
    def wait(seconds: int):
        for i in range(seconds):
            logger.info(f'等待 {seconds - i} 秒')
            time.sleep(1)
        return

    def switch_to_next_window(self):
        logger.info('切换到下一个窗口')
        self.b.switch_to.window(self.b.window_handles[-1])

    def switch_to_last_window(self):
        logger.info('关闭当前窗口，并切换到上一个窗口')
        self.b.close()
        self.b.switch_to.window(self.b.window_handles[0])

    def quit(self):
        self.b.quit()
