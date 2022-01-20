from functools import wraps
from typing import Any, Callable
from time import time

from .exception import Cooling
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
                    raise Cooling(f"还剩{int(lst + tim - t)}秒".format())

            return decorate(func, wrapper)

        return decorator


if __name__ == "__main__":
    import inspect, asyncio

    cm = CoolMaker()

    @cm.cool_async(5)
    async def test(a, b, c=1):
        print(locals())

    async def main():
        await test(1, 2, 3)
        await test(1, 2, 3)

    asyncio.run(main())
