from nonebot import get_driver
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import DBSettings

_driver = get_driver()
_conf = DBSettings(**_driver.config.dict())
Base = declarative_base()

engine = create_engine(
    "postgresql+psycopg2://{}:{}@{}/{}".format(
        _conf.db_user, _conf.db_passwd, _conf.db_addr, _conf.db_name
    ),
    pool_recycle=3600,
    echo=_conf.debug,
    future=True,
)
db = sessionmaker(bind=engine)

AEngine: AsyncEngine = None
ASession: sessionmaker = None

AEngine = create_async_engine(
    "postgresql+asyncpg://{}:{}@{}/{}".format(
        _conf.db_user, _conf.db_passwd, _conf.db_addr, _conf.db_name
    ),
    pool_recycle=3600,
    echo=_conf.debug,
    future=True,
)
ASession = sessionmaker(AEngine, expire_on_commit=False, class_=AsyncSession)

from .global_models import *

Base.metadata.create_all(engine)
