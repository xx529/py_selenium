import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from app.driver import ChromeBrowser
from app.elements import selector

cur_dir = Path().parent

load_dotenv(cur_dir / 'config' / '.env')

if not (data_dir := (cur_dir / 'data')).exists():
    data_dir.mkdir()

with open(cur_dir / 'config' / 'account.txt') as f:
    accounts = [x.strip() for x in f.readlines() if x != '']

start_datetime = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

chrome = ChromeBrowser(selector=selector)
chrome.open('https://union.bytedance.com/open/portal/index/?appId=3000&notHasBroker=&notHasRecruitBroker=')

chrome.click('密码登录')
chrome.send('手机号', os.getenv('ACCOUNT'))
chrome.send('密码', os.getenv('PASSWORD'))
chrome.click('空白处')
chrome.click('确认登录')

chrome.click('左侧弹出框', error='ignore')
chrome.click('主播列表')
chrome.click('右侧弹出框', error='ignore')

df_ls = []
streamer = accounts[0]

chrome.click('搜索主播框')
chrome.send('搜索主播框（激活后）', streamer)
chrome.enter('搜索主播框（激活后）')

chrome.click('主播详情')
chrome.switch_to_next_window()

chrome.click('视频作品')
df = chrome.get_table('作品表格')
df['主播ID'] = streamer
df_ls.append(df)

chrome.switch_to_last_window()
#
# chrome.wait(999)
# chrome.quit()

df_all = pd.concat(df_ls)
df_all.to_csv(f'{str(data_dir / start_datetime)}.csv', index=False)
