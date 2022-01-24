from random import randint, sample, shuffle
from typing import NamedTuple

import pytest
from pydantic import Field
from sqlalchemy import BigInteger, Column, SmallInteger, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import declarative_base
from anyutils.database import models as md
from sqlalchemy.exc import SQLAlchemyError

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


PyUserPerm.check_pk(UserPerm)

string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
key_data = [
    ("".join(sample(string, 10)), "".join(sample(string, 10))) for _ in range(20)
]


async def table(engine: AsyncEngine):
    while True:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


class TestBsModel:
    def test_make_value_raise(self):
        with pytest.raises(AttributeError):
            PyUserPerm.make_value("0")
        with pytest.raises(AttributeError):
            PyUserPerm.make_value("0", ign=("switch",))
        with pytest.raises(AttributeError):
            PyUserPerm.make_value("0", all=("switch",))
        with pytest.raises(md.ChangePrimaryKeyError):
            PyUserPerm.make_value("0", ign=("space",), all=("handle",))
        with pytest.raises(md.ColumnNotFoundError):
            PyUserPerm.make_value("0", ign=("nokey",))
        with pytest.raises(md.ColumnNotFoundError):
            PyUserPerm.make_value("0", all=("nokey",))

    @pytest.mark.asyncio
    async def test_make_value_1(self, Session: sessionmaker, engine: AsyncEngine):
        r = table(engine)
        await anext(r)

        if engine.dialect.name == "sqlite":
            from sqlalchemy.dialects.sqlite import insert
        elif engine.dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import insert
        else:
            pytest.skip(f"不支持数据库{engine.dialect.name}")

        ban = [i for i in range(20)]
        switch = [i for i in range(20)]
        data1 = [
            PyUserPerm(space=i[0][0], handle=i[0][1], ban=i[1], switch=i[2]).dict()
            for i in zip(key_data, ban, switch)
        ]
        async with Session() as session:
            await session.execute(insert(UserPerm.__table__), data1)
            await session.commit()

        switch = [i + 1 for i in switch]
        stmt = insert(UserPerm.__table__)
        stmt = stmt.on_conflict_do_update(
            index_elements=PyUserPerm.__primary_key__,
            set_=PyUserPerm.make_value(stmt, all=("ban",)),
        )
        async with Session() as session:
            await session.execute(
                stmt,
                [
                    PyUserPerm(
                        space=i[0][0], handle=i[0][1], ban=i[1], switch=i[2]
                    ).dict()
                    for i in zip(key_data, ban, switch)
                ],
            )
            await session.commit()

        async with Session() as session:
            res: list[NamedTuple] = (
                await session.execute(select(UserPerm.__table__))
            ).all()
        lis = [PyUserPerm.parse_obj(i) for i in res]
        for i in zip(lis, data1):
            assert i[0].dict() == i[1]

        await anext(r)

    @pytest.mark.asyncio
    async def test_make_value_2(self, Session: sessionmaker, engine: AsyncEngine):
        r = table(engine)
        await anext(r)

        if engine.dialect.name == "sqlite":
            from sqlalchemy.dialects.sqlite import insert
        elif engine.dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import insert
        else:
            raise TypeError(f"不支持数据库{engine.dialect.name}")

        ban = [i for i in range(20)]
        switch = [i for i in range(20)]
        data1 = [
            PyUserPerm(space=i[0][0], handle=i[0][1], ban=i[1], switch=i[2]).dict()
            for i in zip(key_data, ban, switch)
        ]
        async with Session() as session:
            await session.execute(insert(UserPerm.__table__), data1)
            await session.commit()

        switch = [i + 1 for i in switch]
        stmt = insert(UserPerm.__table__)
        stmt = stmt.on_conflict_do_update(
            index_elements=PyUserPerm.__primary_key__,
            set_=PyUserPerm.make_value(stmt, all=("switch",)),
        )
        data2 = [
            PyUserPerm(space=i[0][0], handle=i[0][1], ban=i[1], switch=i[2]).dict()
            for i in zip(key_data, ban, switch)
        ]
        async with Session() as session:
            await session.execute(
                stmt,
                [
                    PyUserPerm(
                        space=i[0][0], handle=i[0][1], ban=i[1], switch=i[2]
                    ).dict()
                    for i in zip(key_data, ban, switch)
                ],
            )
            await session.commit()

        async with Session() as session:
            res: list[NamedTuple] = (
                await session.execute(select(UserPerm.__table__))
            ).all()
        lis = [PyUserPerm.parse_obj(i) for i in res]
        for i in zip(lis, data2):
            assert i[0].dict() == i[1]

        await anext(r)

    def test_pk(self):
        PyUserPerm.check_pk(UserPerm)
        assert PyUserPerm.__primary_key__
        with pytest.raises(md.PrimaryKeyNotEqualError):
            PyUserPerm.check_pk(UserPermWrong)

    @pytest.mark.parametrize("space, handle", key_data)
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

    @pytest.mark.parametrize("space, handle", key_data)
    def test_eq(self, space, handle):
        assert PyUserPerm(
            space=space, handle=handle, ban=randint(1, 100), switch=randint(1, 100)
        ) == PyUserPerm(
            space=space, handle=handle, ban=randint(1, 100), switch=randint(1, 100)
        )
