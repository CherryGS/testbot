from sqlalchemy import create_engine

engine = None

def get_engine(user: str = 'testbot', passwd: str = 'testbot', db: str = 'testbot'):
    global engine
    if engine == None:
        engine = create_engine("postgresql+psycopg2://{}:{}@127.0.0.1:5432/{}".format(user, passwd, db), pool_recycle=3600)
    return engine
