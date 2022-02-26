from admin import sender, locker, LockedError
from httpx import AsyncClient
from nonebot import on_regex
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import RegexMatched
from nonebot.permission import SUPERUSER

from ..exceptions import SourceNotFoundError
from ..initialize import config, get_page, params_screenshot
from .methods import (
    Atc,
    get_contest_screenshot,
    get_editorial_screenshot,
    get_problem_screenshot,
    get_standings_screenshot,
)

problem_screenshot = on_regex(
    "^(abc|arc|agc)[0-9]{3}[a-h](?![a-z])", permission=SUPERUSER, priority=10
)
contest_screenshot = on_regex(
    "^(abc|arc|agc)[0-9]{3}(?![a-z])", permission=SUPERUSER, priority=10
)
standings_screenshot = on_regex(
    "^(abc|arc|agc)[0-9]{3}rk", permission=SUPERUSER, priority=10
)
editorial_screenshot = on_regex(
    "^(abc|arc|agc)[0-9]{3}[a-h]ed", permission=SUPERUSER, priority=10
)


@problem_screenshot.handle()
@sender.catch(Exception, log="未知错误...")
@sender.catch(LockedError, log="冷却中...")
@locker.lock("1")
async def _(matched: str = RegexMatched()):
    contest_prefix = matched[0:3]
    contest_id = matched[3:-1]
    problem_id = matched[-1:]
    img = await get_problem_screenshot(
        Atc(
            contest_prefix=contest_prefix,
            contest_id=contest_id,
            problem_id=problem_id,
        ),
        await get_page(contest_id + problem_id, **params_screenshot),
    )
    await problem_screenshot.send(MessageSegment.image(img))


@contest_screenshot.handle()
@sender.catch(Exception, log="未知错误...")
@sender.catch(LockedError, log="冷却中...")
@locker.lock("1")
async def _(matched: str = RegexMatched()):
    contest_prefix = matched[0:3]
    contest_id = matched[3:]
    img = await get_contest_screenshot(
        Atc(contest_prefix=contest_prefix, contest_id=contest_id),
        await get_page(contest_id, **params_screenshot),
    )
    await contest_screenshot.send(MessageSegment.image(img))


@standings_screenshot.handle()
@sender.catch(Exception, log="未知错误...")
@sender.catch(LockedError, log="冷却中...")
@locker.lock("1")
async def _(matched: str = RegexMatched()):
    if config.atcoder_pswd is None or config.atcoder_user is None:
        await standings_screenshot.finish("该功能需要配置")
    contest_prefix = matched[0:3]
    contest_id = matched[3:-2]
    img = await get_standings_screenshot(
        Atc(contest_prefix=contest_prefix, contest_id=contest_id),
        await get_page(contest_id, **params_screenshot),
        config.atcoder_user,
        config.atcoder_pswd,
    )
    await standings_screenshot.send(MessageSegment.image(img))


@editorial_screenshot.handle()
@sender.catch(Exception, log="未知错误...")
@sender.catch(LockedError, log="冷却中...")
@sender.catch(
    exc=SourceNotFoundError,
    matcher=editorial_screenshot,
    func_msg=lambda y: t if (t := str(y)) else "似乎有什么东西消失了...",
)
@locker.lock("1")
async def _(matched: str = RegexMatched()):
    contest_prefix = matched[0:3]
    contest_id = matched[3:6]
    problem_id = matched[6:7]
    async with AsyncClient() as client:
        img = await get_editorial_screenshot(
            Atc(
                contest_prefix=contest_prefix,
                contest_id=contest_id,
                problem_id=problem_id,
            ),
            client=client,
            page=await get_page(contest_id + problem_id, **params_screenshot),
        )
    await standings_screenshot.send(MessageSegment.image(img))
