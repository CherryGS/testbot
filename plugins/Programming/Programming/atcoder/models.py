from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

Base = declarative_base()


class Contest(Base):  # type: ignore
    __tablename__ = "plugin_atcoder_contest_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contest_name = Column(String)
    contest_url = Column(String)
    start_time = Column(DateTime)
    duration = Column(Integer)
    end_time = Column(DateTime)
