import inspect
import time
from functools import wraps
from typing import Any, Awaitable, Callable, Iterable

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
from nonebot.matcher import Matcher


__all__ = ["sender", "Sender", "sende", "SenderFactory"]

T_Exc = type[Exception] | Iterable[type[Exception]]
T_ExcMsgFunc = Callable[[type[Exception], str | None], str]


class SenderFactory:
    def __init__(
        self,
        *,
        group_id: int | None = None,
        need_pass: tuple[type[Exception], ...] = (),
        bot: Bot | None = None,
    ):
        self.group_id = group_id
        self.need_pass = need_pass
        self.bot = bot

    def __call__(self) -> Any:
        assert self.group_id, "group_id 是必要的"
        return Sender(self.group_id, self.need_pass, self.bot)


class Sender:
    def __init__(
        self,
        group_id: int,
        need_pass: tuple[type[Exception], ...] = (),
        bot: Bot | None = None,
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

    def _generate_exc_msg(
        self,
        e: type[Exception] | Exception,
        log: str | None,
        *,
        custom_: Callable | None,
    ):
        try:
            if custom_ is not None:
                return custom_(e, log)
        except:
            pass
        return log if log is not None else str(type(e)) + str(e)

    def catch(
        self,
        exc: T_Exc,
        log: str | None = None,
        *,
        matcher: type[Matcher] | None = None,
        func_msg: T_ExcMsgFunc | None = None,
    ):
        """捕获并报告选定错误 , 如果添加了 `matcher` 则会调用该 `matcher` 的 `finish` 来发送 msg"""

        def decorater(func: Callable[..., Awaitable[Any]]):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                nonlocal exc
                try:
                    r = await func(*args, **kwargs)
                    return r
                except exc as e:
                    msg = self._generate_exc_msg(e, log, custom_=func_msg)
                    await self._send(msg) if matcher is None else await matcher.finish(
                        msg
                    )
                except Exception as e:
                    if getattr(e, "__sent__", None) is None:
                        msg = self._generate_exc_msg(e, log, custom_=func_msg)
                        await self._send(msg)
                        setattr(e, "__sent__", True)
                    raise

            return wrapper

        return decorater

    def on_raise(self, log: str | None = None, *, func_msg: T_ExcMsgFunc | None = None):
        def decorater(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    r = await func(*args, **kwargs)
                    return r
                except self.need_pass as e:
                    logger.warning(f"异常被忽略 , 信息 {str(type(e)) + str(e)}")
                except Exception as e:
                    if getattr(e, "__sent__", None) is None:
                        msg = self._generate_exc_msg(e, log, custom_=func_msg)
                        await self._send(msg)
                        setattr(e, "__sent__", True)
                    raise

            return wrapper

        return decorater

    def on_call(self, log: str | None = None):
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


sende = SenderFactory(
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
try:
    from .initialize import cfg

    sender = Sender(
        group_id=cfg.reply_group_id,
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
except:
    from nonebot import export

    export.sende = sende
    pass
