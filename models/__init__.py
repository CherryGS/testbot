from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, Boolean
Base = declarative_base()
engine = None
db = type(sessionmaker)

def get_engine(user: str = 'testbot', passwd: str = 'testbot', db: str = 'testbot'):
    global engine
    if engine == None:
        engine = create_engine("postgresql+psycopg2://{}:{}@127.0.0.1:5432/{}".format(user, passwd, db), pool_recycle=3600)
    return engine