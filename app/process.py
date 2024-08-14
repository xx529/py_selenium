import re
from datetime import datetime
from typing import List

import pandas as pd


def normalize_number(x):
    return float(x[:-1]) * 10000 if str(x).endswith('万') else x


def split_datetime(x):
    pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
    result = re.findall(pattern, x)
    return result[-1] if result else ''


def split_title(x):
    return '#'.join(x.split('#')[:-1])


def post_process_platform_data(df: pd.DataFrame):
    df['播放量'] = df['播放量'].apply(normalize_number).astype(int)
    df['推荐播放量'] = df['推荐播放量'].apply(normalize_number).astype(int)
    df['发布日期'] = df['视频'].apply(split_datetime)
    df['视频标题'] = df['视频'].apply(split_title)
    df = df.rename(columns={'播放量': '抖音播放量'})
    df = df.drop_duplicates(subset=['发布日期', '视频标题', '抖音号'], keep='last')
    return df[['发布日期', '视频标题', '抖音号', '抖音播放量', '推荐播放量']]


def get_max_delta_days(ls: List):
    now = datetime.now()
    datetime_ls = [x for x in pd.to_datetime(ls) if x is not pd.NaT]
    delta_days_ls = [(now - x).days for x in datetime_ls]
    if len(delta_days_ls) == 0:
        return 0
    else:
        return max(delta_days_ls)


def pre_process_creator_data(df: pd.DataFrame):
    if '备注' not in df.columns:
        df['备注'] = ''
    df['备注'] = df['备注'].fillna('')
    df = df.dropna(subset=['抖音号']).reset_index(drop=True)
    df['抖音号'] = df['抖音号'].astype(str)
    df['抖音播放量'] = df['抖音播放量'].fillna(0).astype(int)
    df['发布日期'] = df['发布日期'].fillna('').astype(str)
    df.loc[df.duplicated(), '备注'] = '重复'
    return df
