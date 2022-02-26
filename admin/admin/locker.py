from functools import wraps
from typing import Any, Awaitable, Callable, Hashable
from .exc import LockedError

from inspect import stack


class SimpleLocker:
    def __init__(self):
        self.lock_idx = set()

    def _get_caller(self):
        res = stack()[2]
        if res.function == "<module>":
            caller = res.frame.f_globals["__name__"]
        else:
            caller = res.frame.f_globals[res.function]
        return caller

    def set_lock(self, idx: Hashable = None):
        caller = self._get_caller()
        if idx is None:
            idx = caller
        if idx in self.lock_idx:
            raise LockedError(f"{caller} already locked")
        self.lock_idx.add(idx)

    def rm_lock(self, idx: Hashable | None = None):
        caller = self._get_caller()
        if idx is None:
            idx = caller
        self.lock_idx.remove(idx)

    def lock(
        self,
        idx: Hashable = None,
    ):
        def decorator(func: Callable[..., Awaitable[Any]]):
            nonlocal idx
            if idx is None:
                idx = hash(func)

            @wraps(func)
            async def wrapper(*args, **kwargs):
                if idx in self.lock_idx:
                    raise LockedError(f"{func} already locked")
                self.lock_idx.add(idx)
                try:
                    return await func(*args, **kwargs)
                finally:
                    self.lock_idx.remove(idx)

            return wrapper

        return decorator


locker = SimpleLocker()
