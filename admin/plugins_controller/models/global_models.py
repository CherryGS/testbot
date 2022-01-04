from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Boolean, Integer, String
from . import engine, Base

__all__ = []


class pluginsCfg(Base):
    __tablename__ = "_admin_plugins_global_cfg"

    plugin_name = Column(String, unique=True, primary_key=True)
    is_start = Column(Boolean, default=1)

    __mapper_args__ = {"eager_defaults": True}


class pluginsBan(Base):
    __tablename__ = "_admin_plugins_global_ban"

    id = Column(Integer, primary_key=True)
    ban_type = Column(Integer)
    handle = Column(Integer)
    plugin_name = Column(String)

    __mapper_args__ = {"eager_defaults": True}


if __name__ == "__main__":
    pass
