from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from nonebot import get_driver
from pydantic import BaseSettings

driver = get_driver()
config = driver.config


class DBSettings(BaseSettings):

    db_addr: str
    db_name: str
    db_user: str
    db_passwd: str
    debug: bool

    class Config:
        extra = "ignore"


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
