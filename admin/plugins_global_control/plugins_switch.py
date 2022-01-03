from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp import Event
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, on_shell_command, plugins
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.plugin import export
from nonebot.typing import T_State
from nonebot import get_driver
from models.admin.plugins_global_control import pluginsCfg
from models import db
from nonebot.exception import IgnoredException
from nonebot.rule import ArgumentParser
from sqlalchemy import select

driver = get_driver()
conf = driver.config
plugins_settings = dict()


@driver.on_startup
async def _():
    # 存到内存中避免查询开销过大
    qr = select(pluginsCfg.plugin_name, pluginsCfg.is_start)
    with db() as session:
        db_plugins = session.execute(qr).all()
        for i in db_plugins:
            plugins_settings[i.plugin_name] = {}
            plugins_settings[i.plugin_name]["is_start"] = i.is_start

    logger.info("插件开关信息初始化成功")


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    # ignore 掉全局关闭的插件 matcher
    logger.debug("--- ignore ---")
    name = matcher.plugin_name
    if matcher.plugin_name not in plugins_settings.keys():
        return
    if plugins_settings[matcher.plugin_name]["is_start"] == False:
        logger.debug("插件{}被全局禁用".format(name))
        raise IgnoredException("插件{}被全局禁用".format(name))


# -----------------------------------------------------------------------------

cmd1 = on_command("listplugins", priority=1, permission=SUPERUSER)


@cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # 输出插件信息
    tx = str()
    for i in plugins_settings.items():
        tx += "插件名: {}  启用状态: {} \n".format(i[0], bool(i[1]["is_start"]))
    await cmd1.finish(tx)


# -----------------------------------------------------------------------------

parser = ArgumentParser()
parser.add_argument("-p")  # 插件名称 , 将其状态反向

cmd2 = on_shell_command("setplugin", parser=parser, permission=SUPERUSER, priority=1)


@cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # 改变插件状态
    args = state["args"]
    if isinstance(args, Exception):
        await cmd2.finish("参数填写错误 , 请检查")
    name = args.p
    if name not in plugins_settings.keys():
        await cmd2.finish("参数错误 , |{}| 不在插件列表中".format(name))

    session = db()

    qr = select(pluginsCfg).filter(pluginsCfg.plugin_name == name).limit(1)
    try:
        x = session.execute(qr).first()
        x.is_start = plugins_settings[name]["is_start"] ^ True
        plugins_settings[name]["is_start"] ^= True
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("插件状态更改错误")
        await cmd2.send("插件状态更改错误...")
        raise e
    finally:
        session.close()

    logger.info("插件状态更改完成~")
    await cmd2.finish("插件状态更改完成~")
