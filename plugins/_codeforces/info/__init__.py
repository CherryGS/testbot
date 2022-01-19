from nonebot import get_driver
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Event
from nonebot.typing import T_State
from ..models import ASession
from .db_func import *
from .exception import *
from .method import *
from .data_source import *

_cmd1 = on_command("ac", priority=2, permission=SUPERUSER)


@_cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await update_submissions("paekae", 200)

