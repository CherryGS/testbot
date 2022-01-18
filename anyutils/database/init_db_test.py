import asyncio
import pytest as ts

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import BigInteger, Boolean, Integer, String

from init_db import *

Base = declarative_base()


class tb(Base):
    __tablename__ = "_test_table"
    id = Column(Integer, primary_key=True)
    name = Column(Integer)

    def __repr__(self) -> str:
        return f"(id={self.id},name={self.name})"


u1 = "sqlite+aiosqlite:///:memory:"
u2 = "postgresql+asyncpg://testbot:testbot@127.0.0.1:5432/test"

reg.add("sqlite memory", u1, True)
reg.add("sqlite memory", u1, dupli=False)
reg.add("postgres", u2)

reg.init()

engine = reg.get("sqlite memory")

Session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def ins():

    info = [{"id": i, "name": hash(i)} for i in range(100)]
    stmt = insert(tb.__table__)

    async with Session() as session:
        await session.execute(stmt, info)
        await session.commit()


async def que(i):

    stmt = select(tb).where(tb.id == i)

    async with Session() as session:
        res = (await session.execute(stmt)).scalars().all()

    return res[0].name


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ins()
    for i in range(100):
        assert hash(i) == await que(i)


asyncio.run(main())
