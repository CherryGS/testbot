import asyncio
from typing import Any, Callable, Set
from loguru import logger


class HookMaker:
    _hooked_func: Set[Callable[..., Any]]

    def __init__(self, log: str = ""):
        self._log = log
        self._hooked_func = set()

    def add_hook(self, func: Callable[..., Any]) -> Callable[..., Any]:
        self._hooked_func.add(func)
        return func

    async def run_hook(self):
        if self._hooked_func:
            try:
                lis = list(map(lambda x: x(), self._hooked_func))
                await asyncio.gather(*lis)
            except Exception as e:
                logger.opt(exception=e).error("执行Hook {} 时出错".format(self._log))
                raise


if __name__ == "__main__":
    test = HookMaker("test")
    test.run_hook
