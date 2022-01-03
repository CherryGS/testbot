import importlib
from nonebot.plugin import plugins
from nonebot.log import logger
from nonebot import get_driver
from models.admin.plugins_global_control import pluginsCfg
from models import db
from sqlalchemy import select

driver = get_driver()
conf = driver.config


@driver.on_startup
async def _():
    # 初始化插件信息
    logger.debug(str(plugins))
    session = db()
    now_plugins = dict()
    for i in plugins.items():
        if not i[1].export.ignore_global_control:
            now_plugins[i[0]] = i[1]
    db_plugins = session.execute(select(pluginsCfg)).scalars().all()
    try:
        for i in db_plugins:
            if i.plugin_name not in now_plugins.keys():
                session.delete(i)
        name = [_.plugin_name for _ in db_plugins]
        for i in now_plugins.keys():
            if i not in name:
                session.add(pluginsCfg(plugin_name=i))
        session.commit()
    except Exception as e:
        logger.error("插件信息初始化错误")
        raise e
    finally:
        session.close()

    logger.info("插件信息初始化成功")
