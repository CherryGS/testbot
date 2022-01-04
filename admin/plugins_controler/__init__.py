from nonebot.adapters.cqhttp.event import MetaEvent
from nonebot.message import event_preprocessor
from nonebot.plugin import plugins
from nonebot.log import logger
from nonebot import get_driver
from nonebot.plugin import export
from .models.global_models import pluginsCfg
from .config import db
from sqlalchemy import select
from nonebot.adapters.cqhttp import Bot
from .hook import hook
from nonebot.exception import IgnoredException
from .global_controler import *

driver = get_driver()
config = driver.config
is_init = False

export = export()
export.ignore_global_control = True


@event_preprocessor
async def _(bot: Bot, event: Event, state: T_State):
    global is_init
    if not is_init and not isinstance(event, MetaEvent):
        logger.warning("插件数据库初始化未完成 , 事件{}被忽略".format(event))
        raise IgnoredException("")


async def init_db():
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
        logger.info("插件信息初始化成功")
    except Exception as e:
        logger.opt(exception=e).error("插件信息初始化出错")
        raise
    finally:
        session.close()


@driver.on_bot_connect
async def _(bot: Bot):
    global is_init
    if not is_init:
        try:
            await init_db()
            await hook.run_hook()
            is_init = True
        except:
            raise
