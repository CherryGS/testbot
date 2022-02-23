import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker


def pytest_addoption(parser):
    parser.addoption(
        "--dburl",
        action="store",
        default="<if needed, whatever your want>",
        help="url of the database to use for tests",
    )


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine(request):
    db_url = request.config.getoption("--dburl")
    engine: AsyncEngine = create_async_engine(
        db_url,
        future=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def Session(engine: AsyncEngine):
    ASession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield ASession
