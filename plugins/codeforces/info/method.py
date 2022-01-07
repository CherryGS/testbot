from .db_func import *
from .data_source import *


async def get_accept(handle: str, days: int = 30):
    await update_submissions(handle, days)

