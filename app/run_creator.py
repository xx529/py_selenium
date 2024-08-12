from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from app.driver import ChromeBrowser
from app.elements import creator_selector
from app.process import normalize_number, pre_process_creator_data

start_datetime = datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
# cur_dir = Path(__file__).parent.parent
cur_dir = Path().parent.parent

df = pre_process_creator_data(pd.read_excel(cur_dir / 'creator.xlsx'))
df_group = df.groupby('抖音号').agg({'视频标题': list}).reset_index()

chrome = ChromeBrowser(selector=creator_selector, timeout=60)
chrome.open('https://creator.douyin.com/')

chrome.click('平台通知')
chrome.click('达人列表')

for _, (streamer_id, titles) in df_group.iterrows():
    chrome.click('达人列表')
    chrome.click('达人搜索（激活前）')
    chrome.send('达人搜索（激活后）', streamer_id)
    chrome.wait(2)
    if chrome.get_element('搜索弹出框').text == '暂无数据':
        df.loc[df['抖音号'] == streamer_id, '备注'] = '未找到抖音号'
        df.loc[df['抖音号'] == streamer_id, '抖音播放量'] = 0
        continue

    chrome.click('搜索弹出框')
    chrome.wait(1)
    chrome.click('主播详情')
    chrome.click('筛选时间')
    chrome.click('30天')
    chrome.click('空白')
    chrome.wait(2)

    if (total := int(chrome.get_element('视频统计').text.split()[1])) == 0:
        df.loc[df['抖音号'] == streamer_id, '备注'] = '未找到视频'
        df.loc[['抖音号'] == streamer_id, '抖音播放量'] = 0
        continue

    logger.info(f'视频总数：{total}')
    while True:
        details = chrome.get_elements('视频明细')
        logger.info(f'当前视频数：{len(details)}')
        if len(details) >= total:
            break
        else:
            chrome.scroll_to_button()
            chrome.wait(1)

    title2count = {}

    for detail in details:
        title = chrome.get_sub_elements(detail, '视频标题')[0].text
        count = chrome.get_sub_elements(detail, '统计元素')[0].text
        title2count[title] = normalize_number(count)

    for title in titles:
        index = ((df['视频标题'] == title) & (df['抖音号'] == streamer_id))
        if title in title2count:
            df.loc[index, '抖音播放量'] = title2count[title]
        else:
            df.loc[index, '抖音播放量'] = 0
            df.loc[index, '备注'] = '未找到视频'

# from app.elements import creator_selector
# chrome.selector = creator_selector

file = f'{str(cur_dir / start_datetime)}.xlsx'
df.to_excel(file, index=False)
