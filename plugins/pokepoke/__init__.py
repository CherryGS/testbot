from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp.event import PokeNotifyEvent
from nonebot.typing import T_State
from nonebot.plugin import export, on_notice
import random

export = export()

export.ignore_global_control = False

poke_reply = [
    "lsp你再戳？",
    "连个可爱美少女都要戳的肥宅真恶心啊。",
    "你再戳！",
    "？再戳试试？",
    "别戳了别戳了再戳就坏了555",
    "我爪巴爪巴，球球别再戳了",
    "那...那里...那里不能戳...绝对...",
    "(。´・ω・)ん?",
    "欸很烦欸！你戳🔨呢",
    "?",
    "再戳一下试试？",
    "???",
    "正在关闭对您的所有服务...关闭成功",
    "啊呜，太舒服刚刚竟然睡着了。什么事？",
    "正在定位您的真实地址...定位成功。轰炸机已起飞",
    "别戳了..."
]

cmd = on_notice(priority=10)

@cmd.handle()
async def _(bot: Bot, event: PokeNotifyEvent, state: T_State):
    await cmd.finish(random.choice(poke_reply))

