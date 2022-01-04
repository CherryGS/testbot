from .plugins_switch import *
from .plugins_ban import *

from nonebot.plugin import on_message


_bs = on_message(priority=1, block=False)


@_bs.handle()
async def _(bot: Bot, event: Event, state: T_State):
    """注册一个高优先级的事件响应器 , 避免低级同级的 matcher 调用多次 handler

    Args:
        bot (Bot): [description]
        event (Event): [description]
        state (T_State): [description]
    """
    return

