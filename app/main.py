import os
from pathlib import Path

from dotenv import load_dotenv

from driver import ChromeBrowser
from elements import selector

cur_dir = Path().parent

load_dotenv(cur_dir / 'config' / '.env')

if not (path := (cur_dir / 'data')).exists():
    path.mkdir()

print(path.absolute())
print(os.getenv('ACCOUNT'))

# chrome = ChromeBrowser(selector=selector)
# chrome.open('https://union.bytedance.com/open/portal/index/?appId=3000&notHasBroker=&notHasRecruitBroker=')
#
# chrome.click('密码登录')
# chrome.send('手机号', os.getenv('ACCOUNT'))
# chrome.send('密码', os.getenv('PASSWORD'))
# chrome.click('空白处')
# chrome.click('确认登录')
#
# chrome.click('左侧弹出框', error='ignore')
# chrome.click('主播列表')
# chrome.click('右侧弹出框', error='ignore')
# chrome.click('搜索主播框')
# chrome.send('搜索主播框（激活后）', '熟友《七日世界》')
# chrome.enter('搜索主播框（激活后）')
#
# chrome.click('主播详情')
# chrome.switch_to_next_window()
#
# chrome.click('视频作品')
# chrome.switch_to_last_window()
#
# chrome.wait(999)
# chrome.quit()
