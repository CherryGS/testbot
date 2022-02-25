import re
from typing import Any, Hashable

from httpx import AsyncClient
from nonebot import get_driver, on_message
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from playwright.async_api import Page, async_playwright

from ..utils import is_marked
from .method import get_problem_screenshot, get_standings_screenshot

_cached_page: dict[Hashable, Page] = dict()

# 使截图更清晰
screenshot_params = {
    # "viewport": {"width": 1920, "height": 1080},
    "device_scale_factor": 2,
}


async def get_browser():
    async with async_playwright() as dri:
        yield await dri.chromium.launch(headless=False)


browserGenerator = get_browser()


@get_driver().on_startup
async def _():
    global browser
    browser = await anext(browserGenerator)


@get_driver().on_shutdown
async def _():
    global browser
    try:
        await anext(browserGenerator)
    except StopAsyncIteration:
        pass


async def get_page(id: Hashable, **kwargs):
    # * 简单限制缓存大小
    if len(_cached_page) > 10:
        for i in _cached_page:
            await _cached_page.pop(i).close()
    if id not in _cached_page:
        _cached_page[id] = await browser.new_page(**kwargs)
    return _cached_page[id]


regex_1 = re.compile("cf[0-9]+(p[0-9]+){1}")
screenshot_standings = on_message(permission=SUPERUSER, priority=10)


@screenshot_standings.handle()
async def _(marked: str | None = Depends(is_marked(regex_1))):
    if marked is None:
        return
    logger.debug(f"screenshot_standings regex match {marked}")
    [contestId, num] = marked.strip("cf").split("p")
    img = await get_standings_screenshot(
        int(contestId), int(num), page=await get_page(contestId)
    )
    await screenshot_standings.finish(MessageSegment.image(img))


regex_2 = re.compile("cf[0-9]+[a-o]")
screenshot_problem = on_message(permission=SUPERUSER, priority=10)


@screenshot_problem.handle()
async def _(marked: str | None = Depends(is_marked(regex_2))):
    if marked is None:
        return
    logger.debug(f"screenshot_problem regex match {marked}")
    contestId = marked[2:-1]
    idx = marked[-1]
    img = await get_problem_screenshot(
        int(contestId), idx, page=await get_page(contestId)
    )
    await screenshot_problem.finish(MessageSegment.image(img))
