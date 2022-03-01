import asyncio
import inspect
from typing import Any, Awaitable, Callable, Coroutine

from loguru import logger


class HookMaker:
    _hooked_sync_func: list[Callable[..., Any]]
    _hooked_async_func: list[Callable[..., Awaitable[Any]]]

    _hooked_coro: list[Coroutine]

    def __init__(self, log: str = ""):
        self._log = log
        self._hooked_async_func = list()
        self._hooked_sync_func = list()
        self._hooked_coro = list()

    def add_sync_func(self, func: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.isfunction(func) and (
            not inspect.isasyncgenfunction(func)
            and not inspect.iscoroutinefunction(func)
            and not inspect.isgeneratorfunction(func)
        ):
            self._hooked_sync_func.append(func)
            return func
        else:
            raise TypeError("Not sync function")

    def add_async_func(
        self, func: Callable[..., Awaitable[Any]]
    ) -> Callable[..., Awaitable[Any]]:
        if inspect.iscoroutinefunction(func):
            self._hooked_async_func.append(func)
            return func
        else:
            raise TypeError("Not async function")

    def add_coro(self, func):
        if inspect.iscoroutine(func):
            self._hooked_coro.append(func)
        else:
            raise TypeError("Not coroutine")

    def run_sync_func(self, *args, **kwargs) -> list[Any]:
        try:
            return [i(*args, **kwargs) for i in self._hooked_sync_func]
        except Exception as e:
            logger.opt(exception=e).error(f"{self._log}")
            raise

    async def run_async_func(self, *args, **kwargs) -> list[Any]:
        try:
            return list(
                await asyncio.gather(
                    *[i(*args, **kwargs) for i in self._hooked_async_func]
                )
            )
        except Exception as e:
            logger.opt(exception=e).error(f"{self._log}")
            raise

    async def run_coro(self) -> list[Any]:
        try:
            return list(await asyncio.gather(*list(self._hooked_coro)))
        except Exception as e:
            logger.opt(exception=e).error(f"{self._log}")
            raise

    async def run_hook(self, *args, **kwargs) -> tuple[list[Any], ...]:
        return (
            await self.run_async_func(*args, **kwargs),
            await self.run_coro(),
            self.run_sync_func(*args, **kwargs),
        )
