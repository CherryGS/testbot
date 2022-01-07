from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Integer, String
from . import Base, AEngine

__all__ = []


class User(Base):
    __tablename__ = "_plugin_codeforces_user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    handle = Column(String, primary_key=True)
    now_rating = Column(Integer)
    max_rating = Column(Integer)
    last_updated = Column(Integer)

    __mapper_args__ = {"eager_defaults": True}


class BaseSubmission:
    __tablename__ = "_plugin_codeforces_submission_"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_user = Column(String)
    submission_time = Column(BigInteger)
    contest_id = Column(Integer)
    problem_index = Column(Integer)
    problem_name = Column(String)
    verdict = Column(Integer)
    parti_type = Column(Integer)

    __mapper_args__ = {"eager_defaults": True}


async def submission_table_by_name(name: str) -> BaseSubmission:
    bs = "_plugin_codeforces_submission_" + name

    base = declarative_base()

    class Submission(base, BaseSubmission):
        pass

    Submission.__tablename__ = bs
    async with AEngine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    return Submission
