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

    def get(self, name: str) -> Element:
        return self.name2ele.get(name)


selector = ElementSelector(elements=[
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
        key='/html/body/div/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div'
    ),
    Element(
        name='搜索主播框（激活后）',
        key='/html/body/div[1]/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/form/div[1]/div/div/div[2]/div[1]/div/div/input'
    ),
    Element(
        name='主播详情',
        key='/html/body/div/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[4]/div[2]/div/div/div/div/div[1]/div/table/tbody/tr/td[16]/div/div/button[1]/span'
    ),
    Element(
        name='视频作品',
        key='/html/body/div/section/section/section/div/main/div/div/div[2]/div/div/div[2]/div/div[2]/div[4]/div/div/div[1]/div[1]/div[2]/div[5]/div'
    ),
    Element(
        name='作品表格',
        key='semi-table-body',
        by=By.CLASS_NAME
    )
])
