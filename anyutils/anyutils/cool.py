from time import time
from typing import Any, Callable

from decorator import decorate

from .exception import CoolingError


class CoolMaker:
    def __init__(self):
        self.used = []

    def cool_async(
        self,
        tim: int,
        idx: Any = None,
        callback: Callable[[float, int, int, Any, Any], Any] | None = None,
    ):
        lst = 0

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            async def wrapper(func, *args, **kwargs):
                nonlocal tim, lst
                t = time()
                if callback is not None:
                    callback(t, lst, tim, idx, func)
                if lst + tim <= t:
                    lst = t
                    return await func(*args, **kwargs)
                else:
                    raise CoolingError(lst + tim - t, func)

            return decorate(func, wrapper)

        return decorator
