import asyncio
import re
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from pydantic import BaseModel, Field
from tikhub import Client

statistics_cols = ['play_count', 'share_count', 'comment_count', 'digg_count']


class StatisticsData(BaseModel):
    success: bool = Field(False, description='是否下载成功')
    play_count: str | int = Field('-', description='播放数')
    share_count: str | int = Field('-', description='分享数')
    comment_count: str | int = Field('-', description='评论数')
    digg_count: str | int = Field('-', description='点赞数')

    def model_post_init(self, __context: Any) -> None:
        self.play_count = str(self.play_count)
        self.share_count = str(self.share_count)
        self.comment_count = str(self.comment_count)
        self.digg_count = str(self.digg_count)

    @property
    def api_status(self):
        if self.success is True:
            return '成功'
        else:
            return '失败'


async def get_api_data(urls: List[str]) -> Dict[str, StatisticsData]:
    # https://api.tikhub.io/
    async with Client(
            base_url="https://api.tikhub.io",
            api_key="",
            max_retries=10,
            max_connections=100,
            timeout=10,
            max_tasks=50
    ) as client:

        result = {}
        for idx, share_url in enumerate(urls):
            count_str = f'{idx + 1}/{len(urls)}'
            s = time.time()
            try:
                r = await client.DouyinAppV3.fetch_one_video_by_share_url(share_url=share_url)
                success = True
                aweme_id = r['data']['aweme_detail']['statistics']['aweme_id']
                r = await client.DouyinAppV3.fetch_video_statistics(str(aweme_id))
                statistics = r['data']['statistics_list'][0]
                print(count_str, round(time.time() - s, 2), share_url, 'success')
            except Exception as e:
                success = False
                statistics = {}
                print(count_str, round(time.time() - s, 2), share_url, 'fail', str(e))

            data = {'success': success} | statistics
            result[share_url] = StatisticsData.model_validate(data)

    return result


def update_statistics(x, data_dict: Dict[str, StatisticsData]):
    url, *cols_value, api_status = x

    if url not in data_dict:
        return *cols_value, api_status

    data = data_dict[url]
    cur_cols_value = [getattr(data, i) for i in statistics_cols]

    return *cur_cols_value, data.api_status


async def main():
    reset_count = 3
    cur_round = 0

    while reset_count > cur_round:
        cur_round += 1

        cur_dir = Path(__file__).parent.parent
        excel_file = cur_dir / 'share.xlsx'
        df = pd.read_excel(excel_file)

        if 'api数据获取' not in df.columns:
            df['api数据获取'] = '未完成'

        for i in statistics_cols:
            if i not in df.columns:
                df[i] = ''
            df[i] = df[i].fillna('')

        url_pattern = r"https://v\.douyin\.com/\S+"
        df['url'] = df['视频链接'].apply(lambda x: result[0] if (result := re.findall(url_pattern, x)) else '')

        df_select = df[df['api数据获取'] != '成功']

        if len(df_select) == 0:
            break

        api_data = await get_api_data(df_select['url'].tolist())

        df[[*statistics_cols, 'api数据获取']] = df[['url', *statistics_cols, 'api数据获取']].apply(
            lambda x: update_statistics(x, api_data), axis=1, result_type='expand')
        df.to_excel(excel_file, index=False)


if __name__ == '__main__':
    asyncio.run(main())
