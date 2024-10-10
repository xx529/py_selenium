from pathlib import Path

import pandas as pd
from loguru import logger
from selenium.webdriver import Keys

from process import normalize_number
from driver import ChromeBrowser
from elements import platform_selector

cur_dir = Path(__file__).parent.parent
file = cur_dir / 'play.xlsx'

if not (log_dir := cur_dir / 'log').exists():
    log_dir.mkdir()

logger.add('log/play.log', rotation='10 MB')
logger.info('开始 -----------------------------------')

if not file.exists():
    logger.error(f'账号文件不存在：{file}')
    exit(0)

df = pd.read_excel(file, sheet_name=0)
df['抖音号'] = df['抖音号'].astype(str)
df = df.fillna('')
if '备注' not in df.columns:
    df['备注'] = ''

try:
    df_result = pd.read_excel(file, sheet_name=1)
except Exception as e:
    logger.warning('未检测到有结果文件')
    df_result = pd.DataFrame()

if not isinstance(df['开始时间'][0], str):
    df['开始时间'] = df['开始时间'].dt.strftime('%Y-%m-%d')

if not isinstance(df['结束时间'][0], str):
    df['结束时间'] = df['结束时间'].dt.strftime('%Y-%m-%d')

df_data = df[df['备注'] == ''].reset_index(drop=True)
df_data = df_data.drop_duplicates(subset=['抖音号']).reset_index(drop=True)

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
    for idx, (streamer_id, start_datetime, end_datetime) in df_data[['抖音号', '开始时间', '结束时间']].copy(
            deep=True).iterrows():

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

        if try_count == 0:
            index = df['抖音号'] == streamer_id
            df.loc[index, '备注'] = '未找到抖音号'
            logger.warning(f'未找到主播ID：{streamer_id} 跳过该ID ')
            continue

        chrome.click('主播详情')
        chrome.wait(2)
        chrome.switch_to_next_window()

        chrome.click('视频作品')
        chrome.wait(1)

        # 筛选时间
        elements = chrome.get_elements('视频发布日期')
        for i in range(20):
            elements[0].send_keys(Keys.BACKSPACE)
        elements[0].send_keys(start_datetime)
        chrome.wait(1)

        for i in range(20):
            elements[1].send_keys(Keys.BACKSPACE)
        elements[1].send_keys(end_datetime)
        chrome.wait(3)

        total = int(chrome.get_element('总数统计').text.split('·')[-1].replace('个', ''))
        logger.info(f'total: {total}')

        if total == 0:
            index = df['抖音号'] == streamer_id
            df.loc[index, '备注'] = '未找到视频'
            chrome.switch_to_last_window()
            chrome.wait(1)
            continue

        cur_page = 0
        df_res_ls = []

        while True:
            chrome.wait_equal('表格首序号', str(cur_page * 10 + 1))

            df_table = chrome.get_table('作品表格')
            df_table['播放量'] = df_table['播放量'].astype(str).apply(normalize_number)
            df_table['推荐播放量'] = df_table['推荐播放量'].astype(str).apply(normalize_number)
            df_table['抖音号'] = streamer_id
            df_res_ls.append(df_table)

            total -= 10
            if total > 0:
                cur_page += 1
                chrome.click('作品列表下一页')
            else:
                break

        chrome.switch_to_last_window()
        chrome.wait(1)
        index = df['抖音号'] == streamer_id
        df.loc[index, '备注'] = '完成'
        df_result = pd.concat([df_result] + df_res_ls, ignore_index=True)

except Exception as e:
    logger.error(f'发生错误：{e}')
finally:
    chrome.quit()

with pd.ExcelWriter(file) as writer:
    df.to_excel(writer, sheet_name='data', index=False)
    df_result.to_excel(writer, sheet_name='result', index=False)
logger.info(f'完成，数据已更新到：{file}')

logger.info('结束 -----------------------------------')
