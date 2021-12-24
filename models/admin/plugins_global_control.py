from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Boolean, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import models

Base = declarative_base()

class pluginsCfg(Base):
    __tablename__ = '_admin_plugins_global_cfg'

    plugin_name = Column(String(255), unique=True, primary_key=True, comment="插件识别名")
    is_start = Column(Boolean, default=1, comment="插件是否启用")

class pluginsBan(Base):
    __tablename__ = '_admin_plugins_global_ban'

    id = Column(Integer, primary_key=True)
    ban_type = Column(Boolean)
    handle = Column(Integer)
    plugin_name = Column(String(255))

Base.metadata.create_all(models.get_engine())

if __name__ == '__main__':
    pass