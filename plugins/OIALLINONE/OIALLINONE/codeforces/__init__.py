import re
from typing import Any, Hashable

from nonebot import get_driver, on_message
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import Depends
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from playwright.async_api import async_playwright, Page
from httpx import AsyncClient
from ..utils import is_marked
from .method import get_standings_screenshot

_cached_page: dict[Hashable, Page] = dict()

# 使截图更清晰
screenshot_params = {
    "viewport": {"width": 1920, "height": 1080},
    "device_scale_factor": 2,
}


async def get_browser():
    async with async_playwright() as dri:
        yield await dri.chromium.launch()


browserGenerator = get_browser()


@get_driver().on_startup
async def _():
    global browser
    browser = await anext(browserGenerator)


@get_driver().on_shutdown
async def _():
    global browser
    await anext(browserGenerator)


async def get_page(id: Hashable, **kwargs):
    global _cache_page
    if id not in _cached_page:
        _cached_page[id] = await browser.new_page(**kwargs)
    return _cached_page[id]


regex_1 = re.compile("cf[0-9]+(p[0-9]+){0,1}")
sub_1 = re.compile("cf[0-9]+")
screenshot_standings = on_message(permission=SUPERUSER, priority=10)


@screenshot_standings.handle()
async def _(marked: str | None = Depends(is_marked)):
    if marked is None:
        return
    contestId = re.match(sub_1, marked).group()[2:]  # type: ignore
    num = marked[2:].strip(contestId)
    async with AsyncClient() as client:
        img = await get_standings_screenshot(
            int(contestId), int(num), client=client, page=await get_page(contestId)
        )
    await screenshot_standings.finish(MessageSegment.image(img))
