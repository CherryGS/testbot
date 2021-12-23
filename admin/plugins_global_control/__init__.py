from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp import Event
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, plugins, on_shell_command
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.plugin import export
from nonebot.typing import T_State
from utils.sql import get_engine
from sqlalchemy.orm import sessionmaker
from nonebot import get_driver
from . import models
from sqlalchemy.exc import SQLAlchemyError
from nonebot.exception import IgnoredException
from nonebot.rule import ArgumentParser

export = export()
export.ignore_global_control = True


driver = get_driver()
conf = driver.config
db = type(sessionmaker)
plugins_settings = dict()


@driver.on_startup
async def _():
    # 初始化数据库连接
    global db
    engine = get_engine()
    models.Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)

    # 初始化插件信息
    logger.debug(str(plugins))
    session = db()
    now_plugins = dict()
    for i in plugins.items():
        if not i[1].export.ignore_global_control:
            now_plugins[i[0]] = i[1]
    db_plugins = session.query(models.DB).all()
    try:
        for i in db_plugins:
            if i.plugin_name not in now_plugins.keys():
                session.delete(i)
        for i in now_plugins.keys():
            name = [_.plugin_name for _ in db_plugins]
            if i not in name:
                session.add(models.DB(plugin_name=i))
        session.commit()
    except SQLAlchemyError as e:
        session.roll_back()
        logger.error("插件信息初始化错误")
    except Exception as e:
        session.roll_back()
        raise e
    finally:
        session.close()

    # 存到内存中避免查询开销过大
    db_plugins = session.query(models.DB).all()
    global plugins_settings
    for i in db_plugins:
        plugins_settings[i.plugin_name] = i.is_start

    logger.info("插件信息初始化成功")


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    # ignore掉关闭的插件matcher
    name = matcher.plugin_name
    logger.debug(name)
    global plugins_settings
    if matcher.plugin_name not in plugins_settings:
        return
    if plugins_settings[matcher.plugin_name] == False:
        logger.debug("插件{}被全局禁用".format(name))
        raise IgnoredException("插件{}被全局禁用".format(name))


cmd1 = on_command('listplugins', priority=10, permission=SUPERUSER)


@cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # 输出插件信息
    tx = str()
    global plugins_settings
    for i in plugins_settings.items():
        tx += "插件名: {}  启用状态: {} \n".format(i[0], i[1])
    await cmd1.finish(tx)

parser = ArgumentParser()
parser.add_argument('-p')  # 插件名称 , 将其状态反向

cmd2 = on_shell_command('setplugin', parser=parser, permission=SUPERUSER)


@cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # 改变插件状态
    global plugins_settings
    global db
    args = state['args']
    if isinstance(args, Exception):
        await cmd2.finish("参数填写错误 , 请检查")
    name = args.p
    if name not in plugins_settings.keys():
        await cmd2.finish("参数错误 , |{}| 不在插件列表中".format(name))
    

    session = db()

    try:
        x = session.query(models.DB).filter(models.DB.plugin_name == name).first()
        x.is_start = plugins_settings[name] ^ 1
        plugins_settings[name] ^= 1
        session.commit()
    except SQLAlchemyError as e:
        session.roll_back()
        logger.error("插件状态更改错误")
        await cmd2.finish("插件状态更改错误...")
    except Exception as e:
        session.roll_back()
        raise e
    finally:
        session.close()

    logger.info("插件状态更改完成~")
    await cmd2.finish("插件状态更改完成~")

