from models import *

class DB(Base):
    __tablename__ = '_admin_plugins_global_control'

    plugin_name = Column(String(255), unique=True, primary_key=True, comment="插件识别名")
    is_start = Column(Boolean, default=1, comment="插件是否启用")

if __name__ == '__main__':
    pass