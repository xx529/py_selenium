import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from selenium.webdriver.common.by import By

from driver import ChromeBrowser

load_dotenv()

if not (path := Path(os.getenv('DATAPATH'))).exists():
    path.mkdir()

logger.info('打开浏览器')
url = 'https://union.bytedance.com/open/portal/index/?appId=3000&notHasBroker=&notHasRecruitBroker='
chrome = ChromeBrowser(url=url)

logger.info('点击密码登录')
chrome.click('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[3]')

logger.info('输入手机号')
chrome.send('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[2]/div/div/form/div[1]/div/div/input', os.getenv('ACCOUNT'))

logger.info('输入密码')
chrome.send('/html/body/div[1]/div/div[2]/div[4]/div[2]/div[2]/div/div/form/div[2]/div/div/input',
            os.getenv('PASSWORD'))

logger.info('点击空白处')
chrome.click('/html/body/div[1]/div/div[2]/div[4]/div[1]/div')

logger.info('确认登录')
chrome.click('//*[@id="semiTabPanelpassword"]/div/form/button/span')

logger.info('点击弹出框')
chrome.click('/html/body/div[3]/div/div/div[1]/div[2]/div[2]/button/span', error='ignore')

logger.info('手动验证后，点击主播列表')
chrome.click('menu_主播列表', By.ID)

logger.info('点击弹出框')
chrome.click('/html/body/div[3]/div/div/div[1]/div/button/span', error='ignore')

logger.info('输入搜索主播')
chrome.click(
    '/html/body/div/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div')
chrome.send(
    '/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div/div/input',
    '熟友《七日世界》')

logger.info('回车确认')
chrome.enter(
    '/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div/div/input')

logger.info('点击主播详情')
chrome.click(
    '/html/body/div/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[4]/div[2]/div/div/div/div/div[1]/div/table/tbody/tr/td[16]/div/div/button[1]/span')

chrome.switch_to_next_window()
chrome.wait(999)
chrome.quit()
