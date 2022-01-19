from time import time
from typing import List, Tuple
from sqlalchemy.sql.expression import desc, select
from sqlalchemy.sql.functions import func
from .db_func import *
from .data_source import *
from ..models import *

__all__ = [
    "get_rating",
    "get_accept",
    "get_max_rate_prob",
    "get_contest_parti",
    "get_rating_change",
    "get_avatar",
    "get_submissions_count",
]

_status = {0: "OK", 1: "WRONG_ANSWER", 2: "COMPILATION_ERROR", 3: "RUNTIME_ERROR"}

# TODO : 整合


async def get_avatar(handle: str) -> str:
    await update_info(handle)
    session = ASession()
    try:
        res: User = (
            (await session.execute(select(User).where(User.handle == handle).limit(1)))
            .scalars()
            .first()
        )
        return res.title_photo
    except Exception as e:
        raise
    finally:
        await session.close()


async def get_rating(handle: str) -> Tuple[int, int]:
    await update_info(handle)
    session = ASession()
    try:
        res: User = (
            (await session.execute(select(User).where(User.handle == handle).limit(1)))
            .scalars()
            .first()
        )
        if not res:
            return (0, 0)
        return (res.now_rating, res.max_rating)
    except Exception as e:
        raise
    finally:
        await session.close()


async def get_accept(handle: str, days: int = 30) -> int:
    """获取AC数(不重复)

    Args:
        handle (str): 名字
        days (int, optional): 天数. Defaults to 30.

    Returns:
        int: AC数
    """
    await update_submissions(handle, days)
    tab = await get_submission_table_by_name(handle)
    session = ASession()
    try:
        stmt = (
            select(tab.problem_name)
            .where(tab.verdict == _status[0])
            .where(tab.submission_time >= time() - days * 3600 * 24)
        )
        res = (await session.execute(stmt)).all()
        if not res:
            return 0
        return len(res)
    except Exception as e:
        raise
    finally:
        await session.close()


async def get_submissions_count(handle: str, days: int = 30) -> int:
    await update_submissions(handle, days)
    tab = await get_submission_table_by_name(handle)
    session = ASession()
    try:
        stmt = select(func.count(tab.id)).where(
            tab.submission_time >= time() - days * 3600 * 24
        )
        res = (await session.execute(stmt)).scalars().all()
        if not res:
            return 0
        return res[0]
    except Exception as e:
        raise
    finally:
        await session.close()


async def get_max_rate_prob(handle: str, days: int = 30) -> int:
    await update_submissions(handle, days)
    tab = await get_submission_table_by_name(handle)
    session = ASession()
    try:
        stmt = (
            select(Problem)
            .join(
                tab,
                tab.problem_index == Problem.problem_index,
                tab.problem_name == Problem.problem_name,
            )
            .where(tab.submission_time >= time() - days * 3600 * 24)
            .where(tab.verdict == _status[0])
            .order_by(desc(Problem.problem_rating))
            .limit(1)
        )
        res = (await session.execute(stmt)).scalars().first()
        if not res:
            return 0
        return res.problem_rating
    except Exception as e:
        raise
    finally:
        await session.close()


async def get_contest_parti(handle: str, days: int = 30) -> int:
    await update_info(handle)
    session = ASession()
    try:
        stmt = (
            select(func.count(RatingChange.contest_id))
            .join(Contest, RatingChange.contest_id == Contest.contest_id)
            .where(RatingChange.handle == handle)
            .where(Contest.start_time >= time() - days * 3600 * 24)
        )
        res = (await session.execute(stmt)).scalars().all()
        if not res:
            return 0
        return res[0]
    except Exception as e:
        raise
    finally:
        await session.close()


async def get_rating_change(handle: str, days: int = 30) -> int:
    await update_info(handle)
    session = ASession()
    try:
        stmt = (
            select(RatingChange)
            .join(Contest, RatingChange.contest_id == Contest.contest_id)
            .where(RatingChange.handle == handle)
            .where(Contest.start_time >= time() - days * 3600 * 24)
            .order_by(RatingChange.time_second)
        )
        res: List[RatingChange] = (await session.execute(stmt)).scalars().all()
        lis = [i.new_rating - i.old_rating for i in res]
        if not lis:
            return 0
        mx = max(lis)
        mn = min(lis)
        return mx if (mx + mn) >= 0 else mn
    except Exception as e:
        raise
    finally:
        await session.close()
