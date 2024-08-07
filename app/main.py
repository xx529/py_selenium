import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from app.driver import ChromeBrowser
from app.elements import selector

cur_dir = Path().parent

load_dotenv(cur_dir / 'config' / '.env')

if not (data_dir := (cur_dir / 'data')).exists():
    data_dir.mkdir()

with open(cur_dir / 'config' / 'account.txt') as f:
    accounts = [x.strip() for x in f.readlines() if x != '']

logger.info(f'共 {len(accounts)} 个账号，运行时间约{int(len(accounts)/2)}分钟')
logger.info(f'accounts: {accounts}')

start_datetime = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

chrome = ChromeBrowser(selector=selector, timeout=60)
chrome.open('https://union.bytedance.com/open/portal/index/?appId=3000&notHasBroker=&notHasRecruitBroker=')

chrome.click('密码登录')
chrome.send('手机号', os.getenv('ACCOUNT'))
chrome.send('密码', os.getenv('PASSWORD'))
chrome.click('空白处')
chrome.click('确认登录')

chrome.click('左侧弹出框', error='ignore', timeout=5)
chrome.click('主播列表')
chrome.click('跳过引导', error='ignore', timeout=5)
chrome.click('右侧弹出框', error='ignore', timeout=5)

df_ls = []

for streamer_id in accounts:
    logger.info(f'收集主播ID：{streamer_id}')

    chrome.click('搜索主播框')
    chrome.send('搜索主播框（激活后）', streamer_id)
    chrome.wait(2)
    chrome.enter('搜索主播框（激活后）')
    chrome.wait(2)

    try_count = 3
    while True:
        if try_count == 0:
            break

        if chrome.get_element('主播ID').text == streamer_id:
            break
        else:
            logger.info(f'未找到主播ID：{streamer_id}')
            chrome.click('搜索主播框')
            chrome.send('搜索主播框（激活后）', streamer_id)
            chrome.wait(2)
            chrome.enter('搜索主播框（激活后）')
            chrome.wait(2)

        try_count -= 1

    if try_count == 0:
        logger.error(f'未找到主播ID：{streamer_id} 跳过该ID ')
        continue

    chrome.click('主播详情')
    chrome.wait(2)
    chrome.switch_to_next_window()

    chrome.click('视频作品')
    chrome.wait(3)
    total = int(chrome.get_element('总数统计').text.split('·')[-1].replace('个', ''))
    logger.info(f'total: {total}')

    if total == 0:
        continue

    cur_page = 0
    while True:
        chrome.wait_equal('表格首序号', str(cur_page * 10 + 1))

        df = chrome.get_table('作品表格')
        df['主播ID'] = streamer_id
        df_ls.append(df)
        total -= 10

        if total > 0:
            cur_page += 1
            chrome.click('作品列表下一页')
        else:
            break

    chrome.switch_to_last_window()
    chrome.wait(1)

chrome.quit()

df_all = pd.concat(df_ls)
df_all['播放量'] = df_all['播放量'].apply(
    lambda x: float(x[:-1]) * 10000 if str(x).endswith('万') else x).astype(int)
df_all.to_csv(f'{str(data_dir / start_datetime)}.csv', index=False)
logger.info('完成，数据已保存')
