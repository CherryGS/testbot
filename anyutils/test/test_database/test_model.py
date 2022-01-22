from random import sample, randint

import pytest
from pydantic import Field
from sqlalchemy import BigInteger, Column, SmallInteger, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm.decl_api import declarative_base
from src.database import models as md

Base = declarative_base()


class UserPerm(Base):
    __tablename__ = "_admin_user_permissions"

    space = Column(String, primary_key=True)
    handle = Column(String, primary_key=True)
    ban = Column(SmallInteger)
    switch = Column(SmallInteger)


class UserPermWrong(Base):
    __tablename__ = "_admin_user_permissions_1"

    space = Column(String, primary_key=True)
    handle = Column(String)
    ban = Column(SmallInteger)
    switch = Column(SmallInteger)


class PyUserPerm(md.BsModel):

    space: str = Field(pk=True)
    handle: str = Field(pk=True)
    ban: int = 0
    switch: int = 0

    class Config(md.ModelConfig):
        pass


string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
data = [("".join(sample(string, 10)), "".join(sample(string, 10))) for _ in range(20)]


class TestBsModel:
    def test_pk(self):
        PyUserPerm.check_pk(UserPerm)
        with pytest.raises(md.PrimaryKeyNotEqualError):
            PyUserPerm.check_pk(UserPermWrong)

    @pytest.mark.parametrize("space, handle", data)
    def test_hash(self, space, handle):
        assert hash(
            PyUserPerm(
                space=space, handle=handle, ban=randint(1, 100), switch=randint(1, 100)
            )
        ) == hash(
            PyUserPerm(
                space=space, handle=handle, ban=randint(1, 100), switch=randint(1, 100)
            )
        )

    @pytest.mark.parametrize("space, handle", data)
    def test_eq(self, space, handle):
        assert PyUserPerm(
            space=space, handle=handle, ban=randint(1, 100), switch=randint(1, 100)
        ) == PyUserPerm(
            space=space, handle=handle, ban=randint(1, 100), switch=randint(1, 100)
        )
