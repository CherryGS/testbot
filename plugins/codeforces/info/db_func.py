from time import time
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.sql.expression import desc, update

from ..models import (
    ASession,
    Problem,
    User,
    get_submission_table_by_name,
)
from .config import problem, submission, user_info
from .data_source import *

__all__ = [
    "update_info",
    "update_problem",
    "update_submissions",
]


async def update_info(handle: str, force: bool = False) -> None:

    dt = 600
    try:
        session = ASession()
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
        await session.commit()
    except:
        raise
    finally:
        await session.close()


async def update_problem(dict: Dict[str, Any]) -> int:
    try:
        session = ASession()
        src = Problem(**(problem(**dict).dict()))
        await session.merge(src)
        await session.commit()
    except:
        raise
    finally:
        await session.close()


async def update_submissions(handle: str, days: int = 30) -> None:

    await update_info(handle)
    tab = await get_submission_table_by_name(handle)
    try:
        session = ASession()
        newest = (
            (await session.execute(select(tab).order_by(desc(tab.id)).limit(1)))
            .scalars()
            .first()
        )
        if newest:
            oldest = (
                (await session.execute(select(tab).order_by(tab.id).limit(1)))
                .scalars()
                .first()
            )
            res = (await get_submissions_before(handle, newest)) + (
                await get_submissions_days_from(handle, oldest, time(), days)
            )
        else:
            res = await get_submissions_days(handle, time(), days)

        lis = []
        for i in res:
            k = submission(**i)
            lis.append(
                session.merge(
                    tab(
                        **k.dict("problem"),
                        problem_index=k.problem.problem_index,
                        problem_name=k.problem.problem_name
                    )
                )
            )
        await asyncio.gather(*lis)
    except:
        raise
    finally:
        await session.close()
