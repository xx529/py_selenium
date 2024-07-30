import random
import time
from loguru import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ChromeBrowser:

    def __init__(self, url: str):
        self.b = webdriver.Chrome()
        self.b.implicitly_wait(60)
        self.b.get(url)

    def click(self, key: str, method=None, error='raise'):
        try:
            self.get_ele(method, key).click()
            time.sleep(random.random())
        except Exception as e:
            if error == 'ignore':
                pass
            else:
                raise e
        return self

    def send(self, key: str, value: str, method=None):
        self.get_ele(method, key).send_keys(value)
        time.sleep(random.random())
        return self

    def get_ele(self, method, key):
        if method == 'id':
            e = self.b.find_element(by=By.ID, value=key)
        elif method == 'class':
            e = self.b.find_element(by=By.CLASS_NAME, value=key)
        else:
            e = self.b.find_element(by=By.XPATH, value=key)
        return e

    def enter(self, xpath: str):
        self.b.find_element(by=By.XPATH, value=xpath).send_keys(Keys.ENTER)
        time.sleep(random.random())
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


logger.info('打开浏览器')
chrome = ChromeBrowser(
    url='https://union.bytedance.com/open/portal/index/?appId=3000&notHasBroker=&notHasRecruitBroker=')

logger.info('点击密码登录')
chrome.click('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[3]')

logger.info('输入手机号')
chrome.send('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[2]/div/div/form/div[1]/div/div/input', '1')

logger.info('输入密码')
chrome.send('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[2]/div/div/form/div[2]/div/div/input', '1')

logger.info('点击空白处')
chrome.click('/html/body/div[1]/div/div[2]/div[4]/div[1]/div')

logger.info('确认登录')
chrome.click('//*[@id="semiTabPanelpassword"]/div/form/button/span')

logger.info('点击弹出框')
chrome.click('/html/body/div[3]/div/div/div[1]/div[2]/div[2]/button/span', error='ignore')

logger.info('手动验证后，点击主播列表')
chrome.click('menu_主播列表', 'id')

logger.info('点击弹出框')
chrome.click('/html/body/div[3]/div/div/div[1]/div/button/span', error='ignore')

logger.info('输入搜索主播')
chrome.click('/html/body/div/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div')
chrome.send('/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div/div/input', '熟友《七日世界》')

logger.info('回车确认')
chrome.enter('/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div/div/input')

logger.info('点击主播详情')
chrome.click('/html/body/div/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[4]/div[2]/div/div/div/div/div[1]/div/table/tbody/tr/td[16]/div/div/button[1]/span')

chrome.switch_to_next_window()
chrome.wait(999)
chrome.quit()
