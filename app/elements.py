from typing import Any, Dict, List

from pydantic import BaseModel, Field
from selenium.webdriver.common.by import By


class Element(BaseModel):
    name: str = Field(...)
    key: str = Field(...)
    by: str = Field(default=By.XPATH)


class ElementSelector(BaseModel):
    elements: List[Element] = Field(default_factory=list)
    name2ele: Dict[str, Element] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        self.name2ele = {ele.name: ele for ele in self.elements}
        if len(self.name2ele) != len(self.elements):
            raise ValueError('元素名称不能重复')

    def get(self, name: str) -> Element | None:
        return self.name2ele.get(name, None)


platform_selector = ElementSelector(elements=[
    Element(
        name='密码登录',
        key='/html/body/div[1]/div/div[2]/div[4]/div[2]/div[1]/div[3]'
    ),
    Element(
        name='手机号',
        key='/html/body/div[1]/div/div[2]/div[4]/div[2]/div[2]/div/div/form/div[1]/div/div/input'
    ),
    Element(
        name='密码',
        key='/html/body/div[1]/div/div[2]/div[4]/div[2]/div[2]/div/div/form/div[2]/div/div/input'
    ),
    Element(
        name='空白处',
        key='/html/body/div[1]/div/div[2]/div[4]/div[1]/div'
    ),
    Element(
        name='确认登录',
        key='//*[@id="semiTabPanelpassword"]/div/form/button/span'
    ),
    Element(
        name='左侧弹出框',
        key='/html/body/div[3]/div/div/div[1]/div[2]/div[2]/button/span'
    ),
    Element(
        name='主播列表',
        key='menu_主播列表',
        by=By.ID
    ),
    Element(
        name='右侧弹出框',
        key='/html/body/div[3]/div/div/div[1]/div/button/span'
    ),
    Element(
        name='搜索主播框',
        key='/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div/div[2]/form/div[1]/div/div/div[2]/div[1]/div/span'
    ),
    Element(
        name='搜索主播框（激活后）',
        key='/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div/div[2]/form/div[1]/div/div/div[2]/div[1]/div/div/input'
    ),
    Element(
        name='主播详情',
        key='/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div/div[4]/div[2]/div/div/div/div/div[1]/div/table/tbody/tr/td[16]/div/div/button[1]'
    ),
    Element(
        name='主播ID',
        by=By.CLASS_NAME,
        key='semi2-select-option-list'
    ),
    Element(
        name='视频作品',
        key='//*[@id="videoData"]'
    ),
    Element(
        name='主播数据',
        key='//*[@id="liveData"]'
    ),
    Element(
        name='作品表格',
        key='semi-table-body',
        by=By.CLASS_NAME
    ),
    Element(
        name='表格行',
        key='semi-table-row',
        by=By.CLASS_NAME
    ),
    Element(
        name='单元格',
        key='semi-table-row-cell',
        by=By.CLASS_NAME
    ),
    Element(
        name='标题',
        key='span',
        by=By.TAG_NAME
    ),
    Element(
        name='总数统计',
        key='//*[@id="semiTabPanelvideo_data"]/div/div/div[2]/div[1]/div/div[2]'
    ),
    Element(
        name='作品列表下一页',
        key='//*[@id="semiTabPanelvideo_data"]/div/div/div[2]/div[3]/div/div/div/div/div/div/div/div/div[2]/div/ul/li[last()]'
    ),
    Element(
        name='跳过引导',
        key='//*[@id="react-joyride-step-0"]/div/div/div[1]/div[2]/span/button'
    ),
    Element(
        name='表格首序号',
        key='//*[@id="semiTabPanelvideo_data"]/div/div/div[2]/div[3]/div/div/div/div/div/div/div/div/div[1]/div/table/tbody/tr[1]/td[1]/div'
    ),
    Element(
        name='主播列表空白处',
        key='menu_主播列表',
        by=By.ID
    ),
    Element(
        name='曝光展现',
        key='//*[@id="semiTabPanellive_data"]/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div/div[1]/div/div[2]/div[1]/div'
    ),
    Element(
        name='进直播间',
        key='//*[@id="semiTabPanellive_data"]/div/div/div[3]/div[2]/div[1]/div/div/div/div[1]/div/div[2]/div/div[2]/div[1]/div'
    ),
    Element(
        name='观众来源表格',
        # key='webcast-data-browser-component-scene-rich-text-pie-legend',
        key='whitespace-nowrap',
        by=By.CLASS_NAME
    ),
    Element(
        name='观众来源表格-表格行',
        key='items-center',
        by=By.CLASS_NAME
    ),
    Element(
        name='观众来源表格-列名',
        key='mr-2',
        by=By.CLASS_NAME
    ),
    Element(
        name='观众来源表格-数据',
        key='mr-1',
        by=By.CLASS_NAME
    ),
    Element(
        name='日期范围',
        key='//*[@id="anchorDetailContainer"]/div[4]/div/div/div[1]/div[2]/div/span[4]/span'
    ),
    Element(
        name='日期输入',
        key='ant-calendar-input ',
        by=By.CLASS_NAME
    ),
    Element(
        name='视频发布日期',
        key='semi2-input-small',
        by=By.CLASS_NAME
    )
])

creator_selector = ElementSelector(elements=[
    Element(
        name='我是机构',
        key='//*[@id="sub-app"]/div/div[2]/div[3]/div/div[1]/div[2]/div'
    ),
    Element(
        name='达人列表',
        key='//*[@id="root"]/div/div[2]/div[2]/div/div/div/div/ul/li[2]/ul/li[1]'
    ),
    Element(
        name='达人搜索（激活前）',
        key='//*[@id="root"]/div/div/div[2]/div[1]/span/div[2]/div[1]/div/span',
    ),
    Element(
        name='达人搜索（激活后）',
        key='//*[@id="root"]/div/div/div[2]/div[1]/span/div[2]/div[1]/div/div/input'
    ),
    Element(
        name='主播详情',
        key='//*[@id="root"]/div/div/div[3]/div/div/div/div/div/div/div[1]/div/table/tbody/tr/td[6]/div/button'
    ),
    Element(
        name='视频数量',
        key='//*[@id="sub-app"]/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div/div/div/div[1]/div[1]/div/span[1]'
    ),
    Element(
        name='平台通知',
        key='//*[@id="dialog-0"]/div/div[2]/div/div/div[2]/button[1]'
    ),
    Element(
        name='搜索弹出框',
        by=By.CSS_SELECTOR,
        key='.semi-select-option'
    ),
    Element(
        name='筛选时间',
        key='//*[@id="sub-app"]/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div/div/div/div[1]/div[2]/div[1]/button'
    ),
    Element(
        name='7天',
        key='/html/body/div[7]/div/div/div/div/div/div[2]/div[2]/div/div[5]'
    ),
    Element(
        name='14天',
        key='/html/body/div[7]/div/div/div/div/div/div[2]/div[2]/div/div[4]'
    ),
    Element(
        name='30天',
        key='/html/body/div[7]/div/div/div/div/div/div[2]/div[2]/div/div[3]'
    ),
    Element(
        name='90天',
        key='/html/body/div[7]/div/div/div/div/div/div[2]/div[2]/div/div[2]'
    ),
    Element(
        name='时间范围',
        by=By.CSS_SELECTOR,
        key='.btn'
    ),
    Element(
        name='空白',
        key='//*[@id="sub-app"]/div/div[2]/div/div[2]/div/div/div/div/div/div[1]'
    ),
    Element(
        name='视频统计',
        key='//*[@id="sub-app"]/div/div[2]/div/div[2]/div/div/div/div/div/div[2]/div/div/div/div[1]/div[1]/div/span[1]'
    ),
    Element(
        name='视频明细',
        by=By.CLASS_NAME,
        key='video-detail-small'
    ),
    Element(
        name='统计元素',
        key='small-detail-count',
        by=By.CLASS_NAME
    ),
    Element(
        name='视频标题',
        key='detail-title-jump',
        by=By.CLASS_NAME
    )
])
