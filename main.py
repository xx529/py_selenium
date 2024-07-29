import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ChromeBrowser:

    def __init__(self, url: str):
        self.b = webdriver.Chrome()
        self.b.implicitly_wait(10)
        self.b.get(url)

    def click(self, xpath: str):
        self.b.find_element(by=By.XPATH, value=xpath).click()
        time.sleep(random.random())
        return self

    def send(self, xpath: str, value: str):
        self.b.find_element(by=By.XPATH, value=xpath).send_keys(value)
        time.sleep(random.random())
        return self

    def enter(self, xpath: str):
        self.b.find_element(by=By.XPATH, value=xpath).send_keys(Keys.ENTER)
        time.sleep(random.random())
        return self

    def quit(self):
        self.b.quit()


# 打开浏览器
chrome = ChromeBrowser(
    url='https://union.bytedance.com/open/portal/index/?appId=3000&notHasBroker=&notHasRecruitBroker=')

# 点击密码登录
chrome.click('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[3]')

# 输入手机号
chrome.send('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[2]/div/div/form/div[1]/div/div/input', '1')

# 输入密码
chrome.send('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[2]/div/div/form/div[2]/div/div/input', '1')

# 点几空白处
chrome.click('/html/body/div[1]/div/div[2]/div[4]/div[1]/div')

# 确认登录
chrome.click('//*[@id="semiTabPanelpassword"]/div/form/button/span')

# 手动验证后，点击主播列表
chrome.click('/html/body/div/section/section/aside/div/div/div/div[1]/div/ul/li[2]/div[2]/div/ul/li[2]/span/div')

# 点击空白
chrome.click('/html/body/div/section/section/section/div/main/div/div/div[1]/h5')

# 输入搜索主播
chrome.send('/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div/div/input', '熟友《七日世界》')

# 回车确认
chrome.enter('/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div/div/input')


chrome.quit()
