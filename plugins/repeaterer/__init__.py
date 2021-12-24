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
        if dic[id]['content'] == msg:
            if dic[id]['num'] == 3 : 
                flag = True
                dic[id]['num'] = 0
            else : dic[id]['num'] += 1
        else :
            dic[id]['content'] = msg
            dic[id]['num'] = 1
    else: 
        dic[id] = {}
        dic[id]['content'] = msg
        dic[id]['num'] = 1
    if flag :
        await cmd.finish(msg)
    else:
        return