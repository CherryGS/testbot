from io import BytesIO
from nonebot.adapters.cqhttp import Bot, MessageSegment
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.plugin import on_regex
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.exception import *
import random

import os

cmd = on_regex("^\?*$", priority=10)
lis = os.listdir("src/qmark")

@cmd.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    if random.random() < 0.3:
        await cmd.finish('?')
    else:
        res : bytes
        r = random.choice(lis)
        with open('src/qmark/'+r, 'rb') as e:
            res = e.read()
        await cmd.finish(MessageSegment.image(BytesIO(res)))