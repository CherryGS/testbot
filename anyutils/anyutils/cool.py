from functools import wraps
from typing import Any, Callable
from time import time

from .exception import CoolingError
from decorator import decorate


class CoolMaker:
    def __init__(self):
        self.used = []

    def cool_async(self, tim: int):
        lst = 0

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            async def wrapper(func, *args, **kwargs):
                nonlocal tim, lst
                t = time()
                if lst + tim <= t:
                    lst = t
                    return await func(*args, **kwargs)
                else:
                    raise CoolingError(lst + tim - t, func)

            return decorate(func, wrapper)

        return decorator
