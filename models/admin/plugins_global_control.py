from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Boolean, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import models

Base = declarative_base()


class pluginsCfg(Base):
    __tablename__ = "_admin_plugins_global_cfg"

    plugin_name = Column(String, unique=True, primary_key=True)
    is_start = Column(Boolean, default=1)


class pluginsBan(Base):
    __tablename__ = "_admin_plugins_global_ban"

    id = Column(Integer, primary_key=True)
    ban_type = Column(Boolean)
    handle = Column(Integer)
    plugin_name = Column(String)


Base.metadata.create_all(models.engine)

if __name__ == "__main__":
    pass
