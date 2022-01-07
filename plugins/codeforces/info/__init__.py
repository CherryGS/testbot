from nonebot import get_driver

from ..models import ASession
from .db_func import *
from .exception import *

__all__ = []


async def get_accept(handle: str, days: int = 30) -> int:
    await update_submissions(handle, days)

