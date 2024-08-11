from pathlib import Path

import pandas as pd
from loguru import logger

from app.driver import ChromeBrowser
from app.process import pre_process_creator_data
from app.elements import creator_selector

# cur_dir = Path(__file__).parent.parent
cur_dir = Path(__file__).parent.parent

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
        df[df['抖音号'] == streamer_id]['备注'] = '未找到抖音号'
        df[df['抖音号'] == streamer_id]['抖音播放量'] = 0
        continue

    chrome.click('搜索弹出框')
    chrome.wait(1)
    chrome.click('主播详情')
    chrome.click('筛选时间')
    chrome.click('30天')
    chrome.click('空白')
    chrome.wait(2)

    if (total := int(chrome.get_element('视频统计').text.split()[1])) == 0:
        df[df['抖音号'] == streamer_id]['备注'] = '未找到视频'
        df[df['抖音号'] == streamer_id]['抖音播放量'] = 0
        continue

    logger.info(f'视频总数：{total}')
    while True:
        details = chrome.get_elements('视频明细')
        logger.info(f'当前视频数：{len(details)}')
        if len(details) >= total:
            break
        else:
            chrome.scroll_to_button()



from app.elements import creator_selector
chrome.selector = creator_selector