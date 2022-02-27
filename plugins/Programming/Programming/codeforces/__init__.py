from admin import LockedError, sender
from httpx import AsyncClient
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger
from nonebot.params import RegexMatched
from nonebot.permission import SUPERUSER
from anyutils import locker

from ..initialize import get_page, params_screenshot
from ..config import COMMAND_LOCK
from .method import *

standings_screenshot = on_regex(
    "^cf[0-9]+(p[0-9]+){1}", permission=SUPERUSER, priority=10
)
problem_screenshot = on_regex("^cf[0-9]+[a-o]$", permission=SUPERUSER, priority=10)
spstandings_screenshot = on_regex("^cf[0-9]+[ ].*", permission=SUPERUSER, priority=10)
contest_screenshot = on_regex("^cf[0-9]+$", permission=SUPERUSER, priority=10)


@standings_screenshot.handle()
@sender.catch(Exception, log="未知错误...")
@sender.catch(LockedError, log="冷却中...")
@locker.lock(COMMAND_LOCK)
async def _(matched: str = RegexMatched()):
    logger.debug(f"standings_screenshot regex match {matched}")
    [contestId, num] = matched.strip("cf").split("p")
    img = await get_standings_screenshot(
        int(contestId), int(num), page=await get_page(contestId, **params_screenshot)
    )
    await standings_screenshot.send(MessageSegment.image(img))


@problem_screenshot.handle()
@sender.catch(Exception, log="未知错误...")
@sender.catch(LockedError, log="冷却中...")
@locker.lock(COMMAND_LOCK)
async def _(matched: str = RegexMatched()):
    logger.debug(f"problem_screenshotregex match {matched}")
    contestId = matched[2:-1]
    idx = matched[-1]
    img = await get_problem_screenshot(
        int(contestId), idx, page=await get_page(contestId, **params_screenshot)
    )
    await problem_screenshot.send(MessageSegment.image(img))


@spstandings_screenshot.handle()
@sender.catch(Exception, log="未知错误...")
@sender.catch(LockedError, log="冷却中...")
@locker.lock(COMMAND_LOCK)
async def _(matched: str = RegexMatched()):
    params = matched.split(" ")
    contestId = params.pop(0)[2:]
    logger.debug(f"spstandings_screenshot regex match {matched}")
    async with AsyncClient() as client:
        img = await get_spstandings_screenshot(
            params,
            int(contestId),
            client=client,
            page=await get_page(contestId, **params_screenshot),
        )
    await spstandings_screenshot.send(MessageSegment.image(img))


@contest_screenshot.handle()
@sender.catch(Exception, log="未知错误...")
@sender.catch(LockedError, log="冷却中...")
@locker.lock(COMMAND_LOCK)
async def _(matched: str = RegexMatched()):
    logger.debug(f"contest_screenshot regex match {matched}")
    contestId = matched[2:-1]
    img = await get_contest_screenshot(
        int(contestId), page=await get_page(contestId, **params_screenshot)
    )
    await contest_screenshot.send(MessageSegment.image(img))
