from pathlib import Path

import pandas as pd
from loguru import logger

from driver import ChromeBrowser
from elements import platform_selector
from process import pre_process_creator_data, normalize_number

cur_dir = Path(__file__).parent.parent
file = cur_dir / 'platform.xlsx'

if not (log_dir := cur_dir / 'log').exists():
    log_dir.mkdir()

logger.add('log/platform.log', rotation='10 MB')
logger.info('开始 -----------------------------------')

if not file.exists():
    logger.error(f'账号文件不存在：{file}')
    exit(0)

df = pre_process_creator_data(pd.read_excel(file))
df['抖音播放量'] = df['抖音播放量'].fillna(0)
df['推荐播放量'] = df['推荐播放量'].fillna(0)
df_data = df.groupby('抖音号').agg({'视频标题': list, '备注': list, '发布日期': list}).reset_index()
df_data = df_data[df_data['备注'].apply(lambda x: sum([0 if i else 1 for i in x])) > 0]
df_data = df_data.drop('备注', axis=1)
df_data = df_data.reset_index(drop=True)
logger.info('处理数据')

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
    for idx, (streamer_id, titles, publish_datetime_ls) in df_data[['抖音号', '视频标题', '发布日期']].copy(
            deep=True).iterrows():
        logger.info(f'开始第 {idx + 1} 个，抖音号：{streamer_id}')

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
            index = df['抖音号'] == streamer_id
            df.loc[index, '备注'] = '未找到抖音号'
            df.loc[index, '抖音播放量'] = 0
            df.loc[index, '推荐播放量'] = 0
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
            index = df['抖音号'] == streamer_id
            df.loc[index, '备注'] = '未找到视频'
            df.loc[index, '抖音播放量'] = 0
            df.loc[index, '推荐播放量'] = 0
            chrome.switch_to_last_window()
            chrome.wait(1)
            continue

        cur_page = 0
        title2data = {}
        while True:
            chrome.wait_equal('表格首序号', str(cur_page * 10 + 1))
            table = chrome.get_element('作品表格')
            rows = chrome.get_sub_elements(table, '表格行')[1:]

            for row in rows:
                cells = chrome.get_sub_elements(row, '单元格')
                title = cells[1].find_element(by='tag name', value='span').text
                title2data[title] = {
                    '抖音播放量': normalize_number(cells[2].text),
                    '推荐播放量': normalize_number(cells[3].text)
                }

            total -= 10

            if total > 0:
                cur_page += 1
                chrome.click('作品列表下一页')
            else:
                break

        for t in titles:
            index = ((df['视频标题'] == t) & (df['抖音号'] == streamer_id))
            if t in title2data:
                df.loc[index, '备注'] = '完成'
                df.loc[index, '抖音播放量'] = int(title2data[t]['抖音播放量'])
                df.loc[index, '推荐播放量'] = int(title2data[t]['推荐播放量'])
            else:
                df.loc[index, '备注'] = '未找到视频'
                df.loc[index, '抖音播放量'] = 0
                df.loc[index, '推荐播放量'] = 0

        chrome.switch_to_last_window()
        chrome.wait(1)

except Exception as e:
    logger.error(f'发生错误：{e}')
finally:
    chrome.quit()

df.to_excel(file, index=False)
logger.info(f'完成，数据已更新到：{file}')

logger.info('结束 -----------------------------------')
