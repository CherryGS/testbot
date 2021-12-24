from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.plugin import on_message
from nonebot.log import logger
from nonebot.typing import T_State

cmd = on_message(priority=10)
dic = {}

@cmd.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    msg = event.message
    id = event.group_id
    flag = False
    if id in dic.keys():
        if dic[id] == msg:
            flag = True
    dic[id] = msg
    if flag :
        await cmd.finish(msg)
    else:
        return