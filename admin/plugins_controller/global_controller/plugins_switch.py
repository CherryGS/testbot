from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp import Event
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, on_shell_command
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.typing import T_State
from sqlalchemy.sql.expression import update
from ..models import db, ASession
from ..models.global_models import pluginsCfg
from nonebot.exception import IgnoredException
from nonebot.rule import ArgumentParser
from sqlalchemy import select
from ..hook import hook

_plugins_settings = dict()


@hook.add_hook
async def _():
    # 存到内存中避免查询开销过大
    stmt = select(pluginsCfg.plugin_name, pluginsCfg.is_start)
    session = ASession()
    try:
        db_plugins = (await session.execute(stmt)).all()
        for i in db_plugins:
            _plugins_settings[i.plugin_name] = {}
            _plugins_settings[i.plugin_name]["is_start"] = i.is_start
        logger.info("插件开关信息初始化成功")
    except:
        raise
    finally:
        await session.close()


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    # ignore 掉全局关闭的插件 matcher
    logger.debug("--- ignore ---")
    name = matcher.plugin_name
    if matcher.plugin_name not in _plugins_settings.keys():
        return
    if _plugins_settings[matcher.plugin_name]["is_start"] == False:
        logger.info("插件{}被全局禁用".format(name))
        raise IgnoredException("插件{}被全局禁用".format(name))


# -----------------------------------------------------------------------------

_cmd1 = on_command("listplugins", priority=1, permission=SUPERUSER)


@_cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # 输出插件信息
    tx = str()
    for i in _plugins_settings.items():
        tx += "插件名: {}  启用状态: {} \n".format(i[0], bool(i[1]["is_start"]))
    await _cmd1.finish(tx)


# -----------------------------------------------------------------------------

_parser = ArgumentParser()
_parser.add_argument("-p")  # 插件名称 , 将其状态反向

_cmd2 = on_shell_command("setplugin", parser=_parser, permission=SUPERUSER, priority=1)


@_cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # 改变插件状态
    args = state["args"]
    if isinstance(args, Exception):
        await _cmd2.finish("参数填写错误 , 请检查")
    name = args.p
    if name not in _plugins_settings.keys():
        await _cmd2.finish("参数错误 , |{}| 不在插件列表中".format(name))

    session = ASession()

    stmt = (
        update(pluginsCfg)
        .where(pluginsCfg.plugin_name == name)
        .values(is_start=_plugins_settings[name]["is_start"] ^ True)
        .execution_options(synchronize_session=False)
    )
    try:
        await session.execute(stmt)
        _plugins_settings[name]["is_start"] ^= True
        await session.commit()
    except Exception as e:
        await session.rollback()
        await _cmd2.send("插件状态更改错误...")
        raise e
    finally:
        await session.close()

    await _cmd2.finish("插件状态更改完成~")
