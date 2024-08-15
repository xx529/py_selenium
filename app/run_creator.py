from pathlib import Path

import pandas as pd
from loguru import logger

from driver import ChromeBrowser
from elements import creator_selector
from process import get_max_delta_days, normalize_number, pre_process_creator_data

cur_dir = Path(__file__).parent.parent

if not (log_dir := cur_dir / 'log').exists():
    log_dir.mkdir()

logger.add('log/creator.log', rotation='10 MB')
logger.info('开始 -----------------------------------')

file = cur_dir / 'creator.xlsx'
df = pre_process_creator_data(pd.read_excel(file))
df_group = df.groupby('抖音号').agg({'视频标题': list, '备注': list, '发布日期': list}).reset_index()
df_group = df_group[df_group['备注'].apply(lambda x: sum([0 if i else 1 for i in x])) > 0]
df_group = df_group.drop('备注', axis=1)
df_group = df_group.reset_index(drop=True)
logger.info('处理数据')
logger.info(f'共{len(df_group)}个抖音号需要收集')

if len(df_group) == 0:
    logger.info('没有需要执行的抖音号')
    exit(0)

chrome = ChromeBrowser(selector=creator_selector, timeout=60)
chrome.open('https://creator.douyin.com/')

chrome.click('平台通知')
chrome.click('达人列表')

try:
    for idx, (streamer_id, titles, publish_datetime_ls) in df_group.iterrows():
        logger.info(f'开始第 {idx + 1} 个，抖音号：{streamer_id}')
        try:
            chrome.click('达人列表')
            chrome.click('达人搜索（激活前）')
            chrome.send('达人搜索（激活后）', streamer_id)
            chrome.wait(2)
            if chrome.get_element('搜索弹出框', timeout=5).text == '暂无数据':
                logger.warning(f'未找到抖音号：{streamer_id}')
                df.loc[df['抖音号'] == streamer_id, '备注'] = '未找到抖音号'
                df.loc[df['抖音号'] == streamer_id, '抖音播放量'] = 0
                continue

            chrome.click('搜索弹出框')
            chrome.wait(1)
            chrome.click('主播详情')
            chrome.click('筛选时间')

            max_delta_day = get_max_delta_days(publish_datetime_ls)
            logger.info(f'最大天数：{max_delta_day}')
            if max_delta_day <= 7:
                chrome.click('7天')
            elif max_delta_day <= 14:
                chrome.click('14天')
            elif max_delta_day <= 30:
                chrome.click('30天')
            else:
                chrome.click('90天')

            chrome.wait(2)

            if (total := int(chrome.get_element('视频统计').text.split()[1])) == 0:
                logger.warning(f'抖音号({streamer_id})未找到视频')
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
                    df.loc[index, '抖音播放量'] = int(title2count[title])
                    df.loc[index, '备注'] = '完成'
                else:
                    df.loc[index, '抖音播放量'] = 0
                    df.loc[index, '备注'] = '未找到视频'

        except Exception as e:
            logger.error(e)
            logger.error(f'抖音号({streamer_id})异常')

except Exception as e:
    logger.error(e)

logger.info(f'数据更新到：{str(file.absolute())}')
df.to_excel(file, index=False)
logger.info('结束 -----------------------------------')
