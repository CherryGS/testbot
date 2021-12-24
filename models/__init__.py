from sqlalchemy.orm import sessionmaker

from sqlalchemy import create_engine

engine = None
db = type(sessionmaker)


def get_engine(user: str = 'testbot', passwd: str = 'testbot', addr: str = "pgmain:5432", db: str = 'testbot'):
    global engine
    if engine == None:
        engine = create_engine(
            "postgresql+psycopg2://{}:{}@{}/{}".format(user, passwd, addr, db), pool_recycle=3600)
    return engine
