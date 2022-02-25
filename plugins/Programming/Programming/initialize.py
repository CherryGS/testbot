from typing import Hashable

from nonebot import get_driver
from playwright.async_api import Browser, Page, async_playwright

from .config import Config
from uuid import uuid1

config = Config(**get_driver().config.dict())
browser: Browser
cached_page: dict[Hashable, Page] = dict()

# 使截图更清晰
params_screenshot = {
    # "viewport": {"width": 1920, "height": 1080},
    "device_scale_factor": 2,
}


async def get_browser():
    async with async_playwright() as dri:
        yield await dri.chromium.launch()


browserGenerator = get_browser()


async def get_page(id: Hashable = uuid1(), **kwargs):
    # * 简单限制缓存大小
    if len(cached_page) > 10:
        for i in cached_page:
            await cached_page.pop(i).close()
    if id not in cached_page:
        cached_page[id] = await browser.new_page(**kwargs)
    return cached_page[id]


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
