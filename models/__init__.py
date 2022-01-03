from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from nonebot import get_driver
from .config import DBSettings

driver = get_driver()
conf = DBSettings(**driver.config.dict())

engine = create_engine(
    "postgresql+psycopg2://{}:{}@{}/{}".format(
        conf.db_user, conf.db_passwd, conf.db_addr, conf.db_name
    ),
    pool_recycle=3600,
    echo=conf.debug,
    future=True,
)
db = sessionmaker(bind=engine)

