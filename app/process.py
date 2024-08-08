import re

import pandas as pd


def normalize_number(x):
    return float(x[:-1]) * 10000 if str(x).endswith('万') else x


def split_datetime(x):
    pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    result = re.findall(pattern, x)
    return result[-1] if result else ''


def split_title(x):
    return '#'.join(x.split('#')[:-1])


def process_data(df: pd.DataFrame):
    df['播放量'] = df['播放量'].apply(normalize_number).astype(int)
    df['推荐播放量'] = df['推荐播放量'].apply(normalize_number).astype(int)
    df['发布日期'] = df['视频'].apply(split_datetime)
    df['视频标题'] = df['视频'].apply(split_title)
    df = df.rename(columns={'播放量': '抖音播放量'})
    return df[['发布日期', '视频标题', '抖音号', '抖音播放量', '推荐播放量']]
