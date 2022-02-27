from typing import Any, Callable


class AnyUtilsError(Exception):
    pass


class CoolingError(AnyUtilsError):
    """
    当冷却未完成时抛出
    Args:
        `rmtime` : 剩余时间
        `func` : 函数
    """

    def __init__(
        self, rmtime: float | int, func: Callable[..., Any], *args, **kwargs
    ) -> None:
        super().__init__(*args)
        self.rmtime = rmtime
        self.func = func


class LockedError(AnyUtilsError):
    pass
