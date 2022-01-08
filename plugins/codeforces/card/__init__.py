from io import BytesIO
import time
from typing import Any, Dict

from nonebot import on_command
from nonebot.adapters.cqhttp.message import MessageSegment

from ..info import *
from .gen import *
from .level import *
from .utilis import *

_cmd1 = on_command("card", priority=2, permission=SUPERUSER)


@_cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip().split(" ")[1:]  # 用户名
    if len(args) > 0:
        state["handle"] = args


params: Dict[str, Any] = {
    "avatar": [],
    "handle": [],
    "rating": [],
    "accept": [],
    "submision": [],
    "max_rate_problem": [],
    "contest_parti": [],
    "max_rating_change": [],
    "time1": [],
    "time2": [],
}


@_cmd1.got("handle", prompt="输入姓名 , 即得月卡!")
async def _(bot: Bot, event: Event, state: T_State):
    handle = str(state["handle"])
    try:
        rating = await get_rating(handle)
        accept = await get_accept(handle)
        submision = await get_submissions(handle, 30)
        max_rate_problem = await get_max_rate_prob(handle, 30)
        contest_parti = await get_contest_parti(handle, 30)
        max_rating_change = await get_rating_change(handle, 30)
        t1 = time.strftime("%Y-%m-%d", time.localtime())
        t2 = time.strftime("%H:%M:%S", time.localtime())
    except Exception as e:
        await _cmd1.finish(str(e))
    role = await check_rating(rating[0])
    pro = await check_rating(int(max_rate_problem))
    params["handle"] = [handle, role.color]
    params["rating"]
    params["accept"] = [accept, "#000000"]
    params["submision"] = [submision, "#000000"]
    params["max_rate_problem"] = [max_rate_problem, pro.color]
    params["contest_parti"] = [contest_parti, "#000000"]
    params["max_rating_change"] = [
        max_rating_change,
        "#3d3d" if max_rating_change > 0 else "#cccccccc",
    ]
    params["time1"] = [t1, "#b3b3b3b3"]
    params["time2"] = [t2, "#b3b3b3b3"]
    pth1 = r"/home/tickt/project/testbot/plugins/codeforces/card/src/img/card1.png"
    res = month_card_gen(pth1, (await download_img((await get_avatar(handle)))), params)
    await _cmd1.finish(MessageSegment.image(BytesIO(res)))

