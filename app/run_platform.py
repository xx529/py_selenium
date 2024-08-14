from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger

from driver import ChromeBrowser
from elements import platform_selector
from process import post_process_platform_data

cur_dir = Path(__file__).parent.parent
start_datetime = datetime.now().strftime('%Y-%m-%d-%H_%M_%S')

if not (log_dir := cur_dir / 'log').exists():
    log_dir.mkdir()

logger.add('log/platform.log', rotation='10 MB')
logger.info('开始 -----------------------------------')

if not (acc_file := cur_dir / 'platform.xlsx').exists():
    logger.error(f'账号文件不存在：{acc_file}')
    exit(0)

df_data = pd.read_excel(acc_file, dtype='str')
df_data = df_data.drop_duplicates(subset=['抖音号'], ignore_index=True)
if '备注' not in df_data.columns:
    df_data['备注'] = ''
df_data['备注'] = df_data['备注'].fillna('')

if len(df_data) == 0 or sum(df_data['备注'] == '') == 0:
    logger.info('没有需要执行的账号')
    exit(0)

logger.info(f'共 {len(df_data)} 个账号')

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

df_ls = []
drop_streamer_id = None
try:
    for idx, (streamer_id, state) in df_data[['抖音号', '备注']].copy(deep=True).iterrows():
        logger.info(f'开始第：{idx + 1} 个抖音号')

        if state != '':
            logger.info(f'主播ID：{streamer_id} {state}')
            continue

        logger.info(f'收集主播ID：{streamer_id}')
        chrome.click('主播列表空白处')
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
                logger.warning(f'未找到主播ID：{streamer_id}')
                chrome.click('主播列表空白处')
                chrome.wait(1)
                chrome.click('搜索主播框')
                chrome.send('搜索主播框（激活后）', streamer_id)
                chrome.wait(2)
                chrome.enter('搜索主播框（激活后）')
                chrome.wait(2)

            try_count -= 1

        if try_count == 0:
            df_data.loc[idx, '备注'] = '未找到ID'
            logger.warning(f'未找到主播ID：{streamer_id} 跳过该ID ')
            continue

        chrome.click('主播详情')
        chrome.wait(2)
        chrome.switch_to_next_window()

        chrome.click('视频作品')
        chrome.wait(1)
        total = int(chrome.get_element('总数统计').text.split('·')[-1].replace('个', ''))
        logger.info(f'total: {total}')

        if total == 0:
            df_data.loc[idx, '备注'] = '未找到视频'
            chrome.switch_to_last_window()
            chrome.wait(1)
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

        df_data.loc[idx, '备注'] = '完成'
        chrome.switch_to_last_window()
        chrome.wait(1)

except Exception as e:
    drop_streamer_id = streamer_id
    logger.error(f'发生错误：{e}')
finally:
    chrome.quit()

if len(df_ls) == 0:
    logger.warning('未收集到数据')
else:
    file = f'{str(cur_dir / start_datetime)}.xlsx'
    logger.info('数据收集完成')
    df_result = pd.concat(df_ls)

    if drop_streamer_id is not None:
        df_result = df_result[df_result['抖音号'] != drop_streamer_id]

    if len(df_result) == 0:
        logger.warning('未收集到数据')
    else:
        post_process_platform_data(df_result).to_excel(file, index=False)
        logger.info(f'完成，数据已保存到：{file}')

df_data.to_excel(acc_file, index=False)
logger.info('结束 -----------------------------------')
