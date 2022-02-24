from nonebot.adapters.onebot.v11 import Event
from re import Pattern, search


def is_marked(patt: Pattern, event: Event):
    """
    获取原始消息是否完整的被正则式匹配 , 是返回消息 , 否则返回 `None`
    """
    r = search(patt, event.get_plaintext())
    return r if r is None else r.group()
