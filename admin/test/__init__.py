import time
from types import new_class
from typing import List
from nonebot import get_driver
from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import Event, MetaEvent
from nonebot.exception import IgnoredException
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.plugin import export, on_command, plugins, require
from nonebot.typing import T_State
from sqlalchemy import select
from sqlalchemy.sql.expression import update
import asyncio

_req = require("admin.nonebot_plugin_PCtrl")

_test_coolen_async = on_command("testcoolenasync", permission=SUPERUSER, priority=2)

coolen_async = _req.coolen_async


@_test_coolen_async.handle()
@coolen_async(2)
async def _(bot: Bot, event: Event, state: T_State):
    await _test_coolen_async.finish("coolen_async test finished")


_test_coolen_matcher: Matcher = _req.coolen_matcher(
    2, on_command("testcoolenmatcher", permission=SUPERUSER, priority=2)
)


@_test_coolen_matcher.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await _test_coolen_async.send("coolen_matcher test1 finished")


@_test_coolen_matcher.handle()
async def __(bot: Bot, event: Event, state: T_State):
    await _test_coolen_async.finish("coolen_matcher test2 finished")

