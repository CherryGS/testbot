from typing import Dict
from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy.sql import functions as func
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, Date, Float, Integer, String, DateTime
from . import Base, AEngine


class User(Base):
    __tablename__ = "_plugin_codeforces_user"

    handle = Column(String, primary_key=True)
    now_rating = Column(Integer)
    max_rating = Column(Integer)
    friends_count = Column(Integer)
    last_updated = Column(BigInteger)
    title_photo = Column(String)

    __mapper_args__ = {"eager_defaults": True}


class Problem(Base):
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
    verdict = Column(Integer)
    parti_type = Column(Integer)
    contest_id = Column(Integer)
    problem_index = Column(Integer)
    problem_name = Column(String)

    __mapper_args__ = {"eager_defaults": True}


_table: Dict[str, BaseSubmission] = dict()


async def get_submission_table_by_name(name: str) -> BaseSubmission:
    """根据名字动态创建/获取表
    注意 , 该方法不保证用户一定能够存在 , 请进行先验

    Args:
        name (str): [description]

    Returns:
        BaseSubmission: [description]
    """
    global _table

    bs = "_plugin_codeforces_submission_" + name

    if bs in _table.keys():
        return _table[bs]

    base = declarative_base()

    class Submission(base, BaseSubmission):
        __tablename__ = bs

    async with AEngine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    _table[bs] = Submission

    return Submission
