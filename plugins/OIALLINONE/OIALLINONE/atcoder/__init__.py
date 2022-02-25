import re

from nonebot import get_driver, on_message
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from playwright.async_api import async_playwright

from .methods import (
    Atc,
    get_contest_screenshot,
    get_problem_screenshot,
    get_standings_screenshot,
    get_editorial_screenshot,
)
from ..initialize import cfg

driver = get_driver()


@driver.on_startup
async def _():
    global browser, conn
    conn = async_playwright()
    browser = await (await conn.__aenter__()).chromium.launch()


@driver.on_shutdown
async def _():
    global browser, conn
    await browser.close()
    await conn.__aexit__()


regex_1 = re.compile("(abc|arc|agc)[0-9]{3}[a-h](?![a-z])")
screenshot_problom = on_message(permission=SUPERUSER, priority=10)


@screenshot_problom.handle()
async def _(event: Event):
    matched = re.search(regex_1, event.get_plaintext())
    if not matched:
        return
    key = matched.group()
    global browser
    new_page = await browser.new_page()
    img = await get_problem_screenshot(
        Atc(contest_prefix=key[0:3], contest_id=key[3:-1], problem_id=key[-1:]),
        new_page,
    )
    await screenshot_problom.send(MessageSegment.image(img))


regex_2 = re.compile("(abc|arc|agc)[0-9]{3}(?![a-z])")
screenshot_contest = on_message(permission=SUPERUSER, priority=10)


@screenshot_contest.handle()
async def _(event: Event):
    matched = re.search(regex_2, event.get_plaintext())
    if not matched:
        return
    key = matched.group()
    global browser
    new_page = await browser.new_page()
    img = await get_contest_screenshot(
        Atc(contest_prefix=key[0:3], contest_id=key[3:]),
        new_page,
    )
    await screenshot_contest.send(MessageSegment.image(img))


regex_3 = re.compile("(abc|arc|agc)[0-9]{3}rk")
screenshot_standings = on_message(permission=SUPERUSER, priority=10)


@screenshot_standings.handle()
async def _(event: Event):
    matched = re.search(regex_3, event.get_plaintext())
    if not matched:
        return
    key = matched.group()
    global browser
    new_page = await browser.new_page()
    img = await get_standings_screenshot(
        Atc(contest_prefix=key[0:3], contest_id=key[3:-2]),
        new_page,
        cfg.atcoder.username,
        cfg.atcoder.password,
    )
    await screenshot_standings.send(MessageSegment.image(img))


regex_4 = re.compile("(abc|arc|agc)[0-9]{3}[a-h]ed")
screenshot_editorial = on_message(permission=SUPERUSER, priority=10)


@screenshot_editorial.handle()
async def _(event: Event):
    matched = re.search(regex_4, event.get_plaintext())
    if not matched:
        return
    key = matched.group()
    global browser
    new_page = await browser.new_page()
    img = await get_editorial_screenshot(
        Atc(contest_prefix=key[0:3], contest_id=key[3:6], problem_id=key[6:7]),
        new_page,
    )
    await screenshot_standings.send(MessageSegment.image(img))
