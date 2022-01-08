from typing import Dict
from sqlalchemy.orm import relationship

from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, Float, Integer, String
from functools import lru_cache
from . import AEngine, _Base

__all__ = [
    "User",
    "Problem",
    "BaseSubmission",
    "get_submission_table_by_name",
    "RatingChange",
    "Contest",
]


class User(_Base):
    __tablename__ = "_plugin_codeforces_user"

    handle = Column(String, primary_key=True)
    now_rating = Column(Integer)
    max_rating = Column(Integer)
    friends_count = Column(Integer)
    last_updated = Column(BigInteger)
    title_photo = Column(String)

    __mapper_args__ = {"eager_defaults": True}


class Problem(_Base):
    __tablename__ = "_plugin_codeforces_problem"

    contest_id = Column(Integer, primary_key=True)
    problem_index = Column(String, primary_key=True)
    problem_name = Column(String)
    problem_points = Column(Float)
    problem_rating = Column(Float)


class BaseSubmission:
    __tablename__ = "_plugin_codeforces_submission_"

    id = Column(Integer, primary_key=True, autoincrement=False)
    submission_time = Column(BigInteger)
    verdict = Column(String)
    parti_type = Column(String)
    contest_id = Column(Integer)
    problem_index = Column(String)
    problem_name = Column(String)
    # problem = relationship("Problem", backref="prob")

    __mapper_args__ = {"eager_defaults": True}


_tab = dict()


async def get_submission_table_by_name(name: str) -> BaseSubmission:
    """根据名字动态创建/获取表
    注意 , 该方法不保证用户一定能够存在 , 请进行先验

    Args:
        name (str): [description]

    Returns:
        BaseSubmission: [description]
    """
    global _tab

    if name in _tab.keys():
        return _tab[name]

    bs = "_plugin_codeforces_submission_" + name

    base = declarative_base()

    class Submission(base, BaseSubmission):
        __tablename__ = bs

    async with AEngine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    _tab[name] = Submission

    return Submission


class RatingChange(_Base):
    __tablename__ = "_plugin_codeforces_ratingch"

    handle = Column(String, primary_key=True)
    contest_id = Column(Integer, primary_key=True)
    name = Column(String)
    rank = Column(Integer)
    old_rating = Column(Integer)
    new_rating = Column(Integer)
    time_second = Column(BigInteger)
    last_updated = Column(BigInteger)


class Contest(_Base):
    __tablename__ = "_plugin_codeforces_contest"

    contest_id = Column(Integer, primary_key=True)
    name = Column(String)
    start_time = Column(BigInteger)
    last_updated = Column(BigInteger)
