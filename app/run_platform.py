from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from driver import ChromeBrowser
from elements import platform_selector
from process import post_process_platform_data

cur_dir = Path(__file__).parent.parent

ACCOUNT = input('请输入账号：')
PASSWORD = input('请输入密码：')

if not (acc_file := cur_dir / 'account.txt').exists():
    logger.error(f'账号文件不存在：{acc_file}')
    exit(0)

with open(acc_file) as f:
    accounts = [x.strip() for x in f.readlines() if x != '']

logger.info(f'共 {len(accounts)} 个账号，运行时间约{int(len(accounts) / 2)}分钟')
logger.info(f'accounts: {accounts}')

start_datetime = datetime.now().strftime('%Y-%m-%d-%H_%M_%S')

chrome = ChromeBrowser(selector=platform_selector, timeout=60)
chrome.open('https://union.bytedance.com/open/portal/index/?appId=3000&notHasBroker=&notHasRecruitBroker=')

chrome.click('密码登录')
chrome.send('手机号', ACCOUNT)
chrome.send('密码', PASSWORD)
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
    chrome.wait(1)
    total = int(chrome.get_element('总数统计').text.split('·')[-1].replace('个', ''))
    logger.info(f'total: {total}')

    if total == 0:
        continue

    cur_page = 0
    while True:
        chrome.wait_equal('表格首序号', str(cur_page * 10 + 1))

        df = chrome.get_table('作品表格')
        df['抖音号'] = streamer_id
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
logger.info('数据收集完成')

post_process_platform_data(pd.concat(df_ls)).to_excel(f'{str(cur_dir / start_datetime)}.xlsx', index=False)
logger.info('完成，数据已保存')
