import inspect
import time
from functools import wraps

from nonebot import get_bot
from nonebot.adapters import Bot
from nonebot.exception import (
    FinishedException,
    IgnoredException,
    PausedException,
    RejectedException,
    SkippedException,
    StopPropagation,
)
from nonebot.log import logger

from .initialize import cfg

__all__ = ["sender", "SenderFactory"]


class SenderFactory:
    def __init__(
        self,
        group_id: int | None = None,
        need_pass: tuple[type[Exception], ...] = (),
        bot: Bot = None,
    ) -> None:
        self.group_id = group_id
        self.need_pass = need_pass
        self.bot = bot

    async def _send(self, msg: str):
        if not self.bot:
            self.bot = get_bot()
        await self.bot.call_api(
            "send_group_msg",
            group_id=self.group_id,
            message=str(msg),
        )

    def when_raise(self, log: str | None = None):
        def decorater(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    r = await func(*args, **kwargs)
                    return r
                except self.need_pass as e:
                    logger.warning(f"异常被忽略 , 信息 {str(type(e)) + str(e)}")
                except Exception as e:
                    msg = log if log is not None else str(type(e)) + str(e)
                    await self._send(msg)
                    raise

            return wrapper

        return decorater

    def when_func_call(self, log: str | None = None):
        def decorater(func):
            nonlocal log
            if log is None:
                log = str(func.__qualname__) + str(inspect.signature(func))

            @wraps(func)
            async def wrapper(*args, **kwargs):
                msg = (
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    + " "
                    + str(log)
                )
                await self._send(msg)
                return await func(*args, **kwargs)

            return wrapper

        return decorater


sender = SenderFactory(
    group_id=cfg.admin_group_id,
    need_pass=(
        IgnoredException,
        SkippedException,
        FinishedException,
        RejectedException,
        PausedException,
        StopPropagation,
        FinishedException,
    ),
)
