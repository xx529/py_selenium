from pathlib import Path

import pandas as pd

from app.driver import ChromeBrowser
from app.process import pre_process_creator_data
from app.elements import creator_selector

# cur_dir = Path(__file__).parent.parent
cur_dir = Path(__name__).parent.parent

df = pre_process_creator_data(pd.read_excel(cur_dir / 'config' / 'creator.xlsx'))
df_group = df.groupby('抖音号').agg({'视频标题': list}).reset_index()


chrome = ChromeBrowser(selector=creator_selector, timeout=60)
chrome.open('https://creator.douyin.com/')

for _, (streamer_id, titles) in df_group.iterrows():

    chrome.click('达人列表')
    chrome.click('达人搜索（激活前）')
    chrome.send('达人搜索（激活前）', streamer_id)
    chrome.wait(2)
