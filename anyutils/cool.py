from functools import wraps
from typing import Any, Callable
from time import time
from .exception import Cooling


class CoolMaker:
    def __init__(self):
        self.used = []

    def cooling_async(self, tim: int):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            lst = 0

            @wraps(func)
            async def wrapper(*args, **kwargs):
                nonlocal tim, lst
                t = time()
                if lst + tim <= t:
                    lst = t
                    return await func(*args, **kwargs)
                else:
                    raise Cooling("{}".format(int(lst + tim - t)))

            return wrapper

        return decorator
