from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import Event
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor, run_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, require
from nonebot.typing import T_State

_req = require("admin.nonebot_plugin_PCtrl")

_test_coolen_async = on_command("testcoolenasync", permission=SUPERUSER, priority=2)

_coolen_async = _req.coolen_async


@_test_coolen_async.handle()
@_coolen_async(5)
async def _(bot: Bot, event: Event, state: T_State):
    await _test_coolen_async.finish("coolen_async test finished")


_test_coolen_matcher: Matcher = _req.coolen_matcher(
    5, on_command("testcoolenmatcher", permission=SUPERUSER, priority=2)
)


@_test_coolen_matcher.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await _test_coolen_async.send("coolen_matcher test1 finished")


@_test_coolen_matcher.handle()
async def __(bot: Bot, event: Event, state: T_State):
    await _test_coolen_async.finish("coolen_matcher test2 finished")


@run_preprocessor
@_coolen_async(5)
async def _test_run_preprocessor(
    matcher: Matcher, bot: Bot, event: Event, state: T_State
):
    logger.opt(colors=True).warning(" --- test coolen for run_preprocessor ---")


@event_preprocessor
@_coolen_async(5)
async def _test_event_preprocessor(bot: Bot, event: Event, state: T_State):
    logger.opt(colors=True).warning(" --- test coolen for event_preprocessor ---")
