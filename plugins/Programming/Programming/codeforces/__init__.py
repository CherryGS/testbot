from admin import sender
from httpx import AsyncClient
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from nonebot.params import RegexMatched
from nonebot.permission import SUPERUSER

from ..initialize import get_page, params_screenshot
from .method import (
    get_problem_screenshot,
    get_spstandings_screenshot,
    get_standings_screenshot,
)


standings_screenshot = on_regex(
    "^cf[0-9]+(p[0-9]+){1}", permission=SUPERUSER, priority=10
)
problem_screenshot = on_regex("^cf[0-9]+[a-o]", permission=SUPERUSER, priority=10)
spstandings_screenshot = on_regex("^cf[0-9]+[ ].*", permission=SUPERUSER, priority=10)


@standings_screenshot.handle()
async def _(matched: str = RegexMatched()):
    logger.debug(f"screenshot_standings regex match {matched}")
    [contestId, num] = matched.strip("cf").split("p")
    img = await get_standings_screenshot(
        int(contestId), int(num), page=await get_page(contestId, **params_screenshot)
    )
    await standings_screenshot.finish(MessageSegment.image(img))


@problem_screenshot.handle()
async def _(matched: str = RegexMatched()):
    logger.debug(f"screenshot_problem regex match {matched}")
    contestId = matched[2:-1]
    idx = matched[-1]
    img = await get_problem_screenshot(
        int(contestId), idx, page=await get_page(contestId, **params_screenshot)
    )
    await problem_screenshot.finish(MessageSegment.image(img))


@spstandings_screenshot.handle()
async def _(matched: str = RegexMatched()):
    params = matched.split(" ")
    contestId = params.pop(0)[2:]
    logger.debug("screenshot_spstandings regex match {marked}")
    async with AsyncClient() as client:
        img = await get_spstandings_screenshot(
            params,
            int(contestId),
            client=client,
            page=await get_page(contestId, **params_screenshot),
        )
    await spstandings_screenshot.finish(MessageSegment.image(img))
