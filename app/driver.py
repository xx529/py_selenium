import random
import time
from io import StringIO
from typing import List

import pandas as pd
from loguru import logger
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tenacity import retry, stop_after_attempt

from app.elements import ElementSelector


class ChromeBrowser:

    def __init__(self, selector: ElementSelector, timeout=10):
        self.b = webdriver.Chrome()
        self.selector = selector
        self.timeout = timeout

    def open(self, url: str):
        logger.info(f'打开网址：{url}')
        self.b.get(url)
        return self

    def click(self, name: str, error: str = 'raise', timeout: int = None) -> bool:
        logger.info(f'点击`{name}`')
        try:
            self.get_clickable_element(name, timeout).click()
            time.sleep(random.random())
            return True
        except Exception as e:
            if error == 'ignore':
                return False
            else:
                raise e

    def send(self, name: str, value: str):
        logger.info(f'向`{name}`输入`{value}`')
        e = self.get_element(name)
        e.clear()
        e.send_keys(value)
        time.sleep(random.random())
        return self

    @retry(stop=stop_after_attempt(3))
    def get_elements(self, name: str, timeout: int = None) -> List[WebElement]:
        e = self.selector.get(name)
        elements = WebDriverWait(self.b, timeout or self.timeout).until(EC.visibility_of_all_elements_located((e.by, e.key)))
        return elements

    @retry(stop=stop_after_attempt(3))
    def get_element(self, name: str, timeout: int = None) -> WebElement:
        e = self.selector.get(name)
        element = WebDriverWait(self.b, timeout or self.timeout).until(EC.visibility_of_element_located((e.by, e.key)))
        return element

    @retry(stop=stop_after_attempt(3))
    def get_clickable_element(self, name: str, timeout: int = None):
        e = self.selector.get(name)
        element = WebDriverWait(self.b, timeout or self.timeout).until(EC.element_to_be_clickable((e.by, e.key)))
        return element

    def enter(self, name: str):
        logger.info(f'按回车键`{name}`')
        self.send(name, Keys.ENTER)
        return self

    def get_table(self, name: str) -> pd.DataFrame:
        logger.info(f'获取表格`{name}`')
        return pd.read_html(StringIO(self.get_element(name).get_attribute('outerHTML')))[0]

    def wait_equal(self, name: str, value: str):
        logger.info(f'等待`{name}`的值等于`{value}`')
        e = self.selector.get(name)
        WebDriverWait(self.b, self.timeout).until(EC.text_to_be_present_in_element((e.by, e.key), value))
        return self

    @staticmethod
    def wait(seconds: int):
        for i in range(seconds):
            logger.info(f'等待 {seconds - i} 秒')
            time.sleep(1)
        return

    def scroll_to_button(self):
        logger.info('滚动到底部')
        self.b.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def switch_to_next_window(self, wait: int = 2):
        logger.info('切换到下一个窗口')
        time.sleep(wait)
        self.b.switch_to.window(self.b.window_handles[-1])

    def switch_to_last_window(self):
        logger.info('关闭当前窗口，并切换到上一个窗口')
        self.b.close()
        self.b.switch_to.window(self.b.window_handles[0])

    def quit(self):
        logger.info('关闭浏览器')
        self.b.quit()
