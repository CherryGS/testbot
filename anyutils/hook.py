import asyncio
import inspect
from typing import Any, Awaitable, Callable, Coroutine, Set
from loguru import logger


class HookMaker:
    _hooked_async: Set[Callable[..., Any]]
    _hooked_awai: Set[Awaitable]
    _hooked_sync: Set[Callable[..., Any]]

    def __init__(self, log: str = ""):
        self._log = log
        self._hooked_async = set()
        self._hooked_awai = set()
        self._hooked_sync = set()

    def add_hook(self, func: Any) -> Callable[..., Any] | None:
        if inspect.isawaitable(func):
            self._hooked_awai.add(func)
        elif inspect.iscoroutinefunction(func):
            self._hooked_async.add(func)
            return func
        elif inspect.isfunction(func):
            self._hooked_sync.add(func)
            return func
        else:
            raise TypeError("This object can not be hooked")

    async def run_async(self, *args, **kwargs):
        try:
            lis = list(map(lambda x: x(*args, **kwargs), self._hooked_async))
            await asyncio.gather(*lis)
        except Exception as e:
            logger.opt(exception=e).error("执行Hook {} 时出错".format(self._log))
            raise

    async def run_coro(self):
        try:
            await asyncio.gather(*list(self._hooked_awai))
        except Exception as e:
            logger.opt(exception=e).error("执行Hook {} 时出错".format(self._log))
            raise

    async def run_sync(self, *args, **kwargs):
        try:
            for i in self._hooked_sync:
                i(*args, **kwargs)
        except Exception as e:
            logger.opt(exception=e).error("执行Hook {} 时出错".format(self._log))
            raise

    async def run_hook(self, *args, **kwargs):
        await asyncio.gather(
            *[
                self.run_async(*args, **kwargs),
                self.run_coro(),
                self.run_sync(*args, **kwargs),
            ]
        )


if __name__ == "__main__":
    test = HookMaker("test")
    test.run_hook
