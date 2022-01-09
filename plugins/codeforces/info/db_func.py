import asyncio
from time import time
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.sql.expression import desc, update

from ..models import *
from .config import *
from .data_source import *

__all__ = [
    "update_info",
    "update_problem",
    "update_submissions",
    "update_rating_list",
    "update_contest",
]


async def update_info(handle: str, force: bool = False) -> None:
    """更新用户信息 , 如果不存在尝试创建

    Args:
        handle (str): 用户名
        force (bool, optional): 是否强制更新. Defaults to False.
    """
    # * 更新最小时间间隔
    dt = 600
    session = ASession()
    try:
        res: User = (
            (await session.execute(select(User).where(User.handle == handle).limit(1)))
            .scalars()
            .first()
        )
        c = await get_user_info(handle)
        if not res:
            session.add(User(**user_info(**c).dict()))
        elif force or (time() - res.last_updated > dt):
            await session.execute(
                update(User)
                .where(User.handle == res.handle)
                .values(**user_info(**c).dict(exclude={"handle"}))
            )
        else:
            return
        await update_rating_list(handle)
        await update_contest(handle)
        await session.commit()
    except:
        raise
    finally:
        await session.close()


async def update_problem(dict: Dict[str, Any]):
    session = ASession()
    try:
        src = Problem(**(problem(**dict).dict()))
        await session.merge(src)
        await session.commit()
    except:
        raise
    finally:
        await session.close()


async def update_submissions(handle: str, days: int = 30) -> None:
    """更新某人提交记录 , 如果用户不存在会尝试创建

    Args:
        handle (str): 名字
        days (int, optional): 天数. Defaults to 30.
    """

    await update_info(handle)
    tab = await get_submission_table_by_name(handle)
    session = ASession()
    try:
        newest: BaseSubmission = (
            (await session.execute(select(tab).order_by(desc(tab.id)).limit(1)))
            .scalars()
            .first()
        )
        if newest:
            oldest: BaseSubmission = (
                (await session.execute(select(tab).order_by(tab.id).limit(1)))
                .scalars()
                .first()
            )
            res = (await get_submissions_before(handle, newest.id)) + (
                await get_submissions_days_from(handle, oldest.id, time(), days)
            )
        else:
            res = await get_submissions_days(handle, time(), days)

        # ! Submission 更新之处 / Problem with
        for i in res:
            k = submission(**i)
            await session.merge(
                tab(
                    **k.dict(exclude={"problem", "author"}),
                    problem_index=k.problem.problem_index,
                    problem_name=k.problem.problem_name,
                    parti_type=k.author.parti_type
                )
            )
            await session.merge(Problem(**k.problem.dict()))
        await session.commit()
    except:
        raise
    finally:
        await session.close()


async def update_rating_list(handle: str):
    # TODO : 优化
    res = await get_rating_list(handle)
    session = ASession()
    try:

        for i in res:
            await session.merge(RatingChange(**ratingch(**i).dict()))
        await session.commit()
    except Exception as e:
        raise
    finally:
        await session.close()


async def update_contest(handle: str):
    # TODO : 优化
    res = await get_contest_list(handle)
    session = ASession()
    try:
        for i in res:
            await session.merge(Contest(**contest(**i).dict()))
        await session.commit()
    except Exception as e:
        raise
    finally:
        await session.close()
