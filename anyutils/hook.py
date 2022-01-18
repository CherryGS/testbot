import asyncio
import inspect
from typing import Any, Awaitable, Callable, Coroutine, Set
from loguru import logger


class HookMaker:
    _hooked_func: Set[Callable[..., Any]]
    _hooked_awai: Set[Awaitable]

    def __init__(self, log: str = ""):
        self._log = log
        self._hooked_func = set()
        self._hooked_awai = set()

    def add_hook(self, func: Any) -> Callable[..., Any] | None:
        if inspect.isawaitable(func):
            self._hooked_awai.add(func)
        elif inspect.iscoroutinefunction(func):
            self._hooked_func.add(func)
            return func

    async def run_hook(self, *args, **kwargs):
        try:
            lis = list(map(lambda x: x(*args, **kwargs), self._hooked_func))
            await asyncio.gather(*lis + list(self._hooked_awai))
        except Exception as e:
            logger.opt(exception=e).error("执行Hook {} 时出错".format(self._log))
            raise


if __name__ == "__main__":
    test = HookMaker("test")
    test.run_hook
