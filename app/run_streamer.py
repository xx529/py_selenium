from pathlib import Path

import pandas as pd
from loguru import logger
from selenium.webdriver import Keys

from driver import ChromeBrowser
from elements import platform_selector
from process import normalize_number

cur_dir = Path(__file__).parent.parent
file = cur_dir / 'streamer.xlsx'

if not (log_dir := cur_dir / 'log').exists():
    log_dir.mkdir()

logger.add('log/streamer.log', rotation='10 MB')
logger.info('开始 -----------------------------------')

if not file.exists():
    logger.error(f'账号文件不存在：{file}')
    exit(0)

df = pd.read_excel(file)
df = df.fillna('')
df['抖音号'] = df['抖音号'].astype(str)
if '备注' not in df.columns:
    df['备注'] = ''

if not isinstance(df['开始时间'][0], str):
    df['开始时间'] = df['开始时间'].dt.strftime('%Y-%m-%d')

if not isinstance(df['结束时间'][0], str):
    df['结束时间'] = df['结束时间'].dt.strftime('%Y-%m-%d')

df_data = df[df['备注'] == ''].reset_index(drop=True)

if len(df_data) == 0:
    logger.info('没有需要执行的账号')
    exit(0)

logger.info(f'共{len(df_data)}个抖音号需要收集')

ACCOUNT = input('请输入账号：')
PASSWORD = input('请输入密码：')

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

try:
    for idx, streamer_id in enumerate(df_data['抖音号'].tolist()):

        try_count = 3
        while True:
            if try_count == 0:
                break

            chrome.click('主播列表空白处')
            chrome.click('搜索主播框')
            chrome.send('搜索主播框（激活后）', streamer_id)
            chrome.wait(2)

            if streamer_id in chrome.get_element('主播ID').text:
                chrome.enter('搜索主播框（激活后）')
                chrome.wait(2)
                break
            else:
                logger.warning(f'未找到主播ID：{streamer_id}')
                try_count -= 1
                continue

        index = df['抖音号'] == streamer_id
        if try_count == 0:
            df.loc[index, '备注'] = '未找到抖音号'
            logger.warning(f'未找到主播ID：{streamer_id} 跳过该ID ')
            continue

        chrome.click('主播详情')
        chrome.wait(2)
        chrome.switch_to_next_window()

        chrome.click('主播数据')
        chrome.wait(1)

        chrome.click('日期范围')
        elements = chrome.get_elements('日期输入')

        for i in range(20):
            elements[0].send_keys(Keys.BACKSPACE)
        elements[0].send_keys(df[df['抖音号'] == streamer_id]['开始时间'].tolist()[0])
        chrome.wait(1)

        for i in range(20):
            elements[1].send_keys(Keys.BACKSPACE)
        elements[1].send_keys(df[df['抖音号'] == streamer_id]['结束时间'].tolist()[0])

        chrome.wait(1)
        elements[1].send_keys(Keys.ENTER)

        chrome.wait(3)
        df.loc[index, '曝光展现'] = normalize_number(chrome.get_element('曝光展现').text.replace('人', ''))
        df.loc[index, '进直播间'] = normalize_number(chrome.get_element('进直播间').text.replace('人', ''))
        df.loc[index, '直播推荐'] = 0
        df.loc[index, '视频推荐'] = 0
        df.loc[index, '其他'] = 0
        df.loc[index, '搜索'] = 0
        df.loc[index, '关注'] = 0
        df.loc[index, '同城'] = 0
        df.loc[index, '个人主页'] = 0
        df.loc[index, '商业化'] = 0

        if int(normalize_number(chrome.get_element('曝光展现').text.replace('人', ''))) == 0:
            df.loc[index, '备注'] = '没有数据'
        else:
            for e in chrome.get_elements('观众来源表格'):
                name = chrome.get_sub_elements(e, '观众来源表格-列名')[0].text
                value = chrome.get_sub_elements(e, '观众来源表格-数据')[0].text
                df.loc[index, name] = value
            df.loc[index, '备注'] = '完成'

        chrome.switch_to_last_window()
        chrome.wait(1)

except Exception as e:
    logger.error(f'发生错误：{e}')
finally:
    chrome.quit()

df.to_excel(file, index=False)
logger.info(f'完成，数据已更新到：{file}')

logger.info('结束 -----------------------------------')
