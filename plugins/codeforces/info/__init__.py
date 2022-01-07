# 拿数据
from ..models import user as usr
from nonebot import get_driver

_driver = get_driver()


@_driver.on_startup
async def _():
    k = await usr.submission_table_by_name("paekae")
    print(k)
