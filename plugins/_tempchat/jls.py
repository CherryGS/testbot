from io import BytesIO
from nonebot.adapters.cqhttp import Bot, MessageSegment
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.plugin import on_keyword
from nonebot.typing import T_State
import random
from nonebot.plugin import require
import os

_req = require("admin.nonebot_plugin_PCtrl")

_cmd = _req.coolen_matcher(5, on_keyword({"jls", "jiangly"}, priority=10))
_lis = os.listdir("src/jls")


@_cmd.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if random.random() < 0.1:
        await _cmd.finish("This is jiangly fans club")
    res: bytes
    r = random.choice(_lis)
    with open("src/jls/" + r, "rb") as e:
        res = e.read()
    await _cmd.finish(MessageSegment.image(BytesIO(res)))
