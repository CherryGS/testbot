from io import BytesIO
from pathlib import Path
import time
from typing import Any, Dict
from nonebot.plugin import require

from nonebot import on_command
from nonebot.adapters.cqhttp.message import MessageSegment


from ..info import *
from .gen import *
from .level import *
from .utils import *

_req = require("admin.nonebot_plugin_PCtrl")
_cool = _req.coolen_matcher  # type: ignore
_cmd1 = _cool(60, on_command("card", priority=2))


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
    timA = time.time()
    try:
        rating = await get_rating(handle)
        accept = await get_accept(handle)
        submision = await get_submissions_count(handle, 30)
        max_rate_problem = await get_max_rate_prob(handle, 30)
        contest_parti = await get_contest_parti(handle, 30)
        max_rating_change = await get_rating_change(handle, 30)
        t1 = time.strftime("%Y-%m-%d", time.localtime())
        t2 = time.strftime("%H:%M:%S", time.localtime())
        role = await check_rating(rating[0])
        pro = await check_rating(int(max_rate_problem))
        params["handle"] = ColorString(text=handle, color=role.color)
        params["rating"] = (
            ColorString(text="rating: ", color="#000000")
            + ColorString(text=rating[0], color=role.color)
            + ColorString(text=" (with ", color="#000000")
            + ColorString(text=rating[1], color=role.color)
            + ColorString(text=" max)", color="#000000")
        )
        params["accept"] = ColorString(text=accept, color="#000000")
        params["submision"] = ColorString(text=submision, color="#000000")
        params["max_rate_problem"] = ColorString(text=max_rate_problem, color=pro.color)
        params["contest_parti"] = ColorString(text=contest_parti, color="#000000")
        params["max_rating_change"] = ColorString(
            text=max_rating_change,
            color=(
                "#3d3d"
                if max_rating_change > 0
                else ("#000000" if max_rating_change == 0 else "#c70803")
            ),
        )
        params["time1"] = ColorString(text=t1, color="#000000")
        params["time2"] = ColorString(text=t2, color="#000000")
        pth = r"/home/tickt/project/testbot/plugins/codeforces/card/src/img/card1.png"
        ava_url = await get_avatar(handle)
        ava = await download_img(ava_url)
        month_card_gen(
            pth,
            ava,
            params,
            "/home/tickt/project/testbot/plugins/codeforces/card/test.jpg",
        )
    except Exception as e:
        await _cmd1.send(str(e))
        raise e
    timB = time.time()
    await _cmd1.send("gen card in {} senonds".format(int(timB - timA)))
    await _cmd1.finish(
        MessageSegment.image(
            Path("/home/tickt/project/testbot/plugins/codeforces/card/test.jpg")
        )
    )

