from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, plugins, on_shell_command
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.typing import T_State
from nonebot import get_driver
from sqlalchemy import select
from models.admin.plugins_global_control import pluginsBan, pluginsCfg
from models import db
from nonebot.exception import IgnoredException
from nonebot.rule import ArgumentParser
from sqlalchemy.exc import SQLAlchemyError

driver = get_driver()
conf = driver.config
ban_settings = {0: {}, 1: {}}


@driver.on_startup
async def _():

    # 加载全局ban
    try:
        session = db()
        qr = select(pluginsBan)
        ban = session.execute(qr).scalars().all()
        global ban_settings
        for i in ban:
            ban_settings |= {i.ban_type: {i.handle: {i.plugin_name: {}}}}
        logger.info("全局ban初始化成功")
    except:
        logger.error("全局ban初始化失败")
        raise
    finally:
        session.close()


# -----------------------------------------------------------------------------


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    # ignore掉全局被ban的人/群的matcher
    logger.debug("--- ban ---")
    handle_qq = event.user_id
    name = matcher.plugin_name
    if handle_qq in ban_settings[0] and name in ban_settings[0][handle_qq]:
        logger.debug("QQ号:{}被全局ban".format(handle_qq))
        raise IgnoredException("QQ号:{}被全局ban".format(handle_qq))

    if isinstance(event, GroupMessageEvent):
        handle_gr = event.group_id
        if handle_gr in ban_settings[1] and name in ban_settings[1][handle_gr]:
            logger.debug("群号:{}被全局ban".format(handle_gr))
            raise IgnoredException("群号:{}被全局ban".format(handle_gr))


# -----------------------------------------------------------------------------

parser = ArgumentParser()
parser.add_argument("-u")  # 个人 qq 号
parser.add_argument("-g")  # 群号
parser.add_argument("-p")  # 插件名

cmd1 = on_shell_command("ban", parser=parser, permission=SUPERUSER)


@cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # ban 人/群
    args = state["args"]
    if isinstance(args, Exception):
        await cmd1.finish("参数填写错误 , 请检查")

    if args.u and args.g:
        await cmd1.finish("个人和群只能选择一个")

    if not args.u and not args.g:
        await cmd1.finish("个人和群必须选择一个")

    with db() as session:
        if not session.execute(
            select(pluginsCfg).filter(pluginsCfg.plugin_name == args.p).limit(1)
        ):
            await cmd1.finish("参数错误 , |{}| 不在插件列表中".format(args.p))

    ban_type = 0
    handle: int
    name = args.p
    global ban_settings

    if args.g:
        ban_type = 1
        handle = int(args.g)
    else:
        ban_type = 0
        handle = int(args.u)

    session = db()
    try:
        session.add(pluginsBan(ban_type=ban_type, handle=handle, plugin_name=name))
        session.commit()
        ban_settings |= {ban_type: {handle: {name: {}}}}
        logger.info("ban执行成功")
        await cmd1.finish("ban执行成功")
    except SQLAlchemyError as e:
        logger.error("向数据库中添加ban时出现异常\n 异常信息 : \n {}".format(e))
        await cmd1.finish("向数据库中添加ban时出现异常\n 异常信息 : \n {}".format(e))
    finally:
        session.close()


# -----------------------------------------------------------------------------

parser = ArgumentParser()
parser.add_argument("-u")  # 个人 qq 号
parser.add_argument("-g")  # 群号
parser.add_argument("-p")  # 插件名

cmd2 = on_shell_command("unban", parser=parser, permission=SUPERUSER)


@cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # unban 人/群
    args = state["args"]
    if isinstance(args, Exception):
        await cmd2.finish("参数填写错误 , 请检查")

    if (args.u and args.g) or (not args.u and not args.g):
        await cmd2.finish("个人和群只能选择一个")

    session = db()
    qr = select(pluginsCfg).filter(pluginsCfg.plugin_name == args.p).limit(1)
    if not session.execute(qr).first():
        await cmd2.finish("参数错误 , |{}| 不在插件列表中".format(args.p))

    ban_type = 0
    handle: int
    name = args.p
    global ban_settings

    if args.g:
        ban_type = True
        handle = int(args.g)
    else:
        ban_type = False
        handle = int(args.u)

    if (handle in ban_settings[ban_type]) and (name in ban_settings[ban_type][handle]):
        session = db()
        try:
            ban_settings[ban_type][handle].pop(name)
            qr = (
                select(pluginsBan)
                .filter(
                    pluginsBan.ban_type == ban_type,
                    pluginsBan.handle == handle,
                    pluginsBan.plugin_name == name,
                )
                .limit(1)
            )
            res = session.execute(qr).scalars().all()
            session.delete(res[0])
            session.commit()
            logger.info("unban执行成功")
            await cmd2.finish("unban执行成功")
        except SQLAlchemyError as e:
            logger.error("unban时出现异常\n 异常信息 : \n {}".format(e))
            await cmd1.finish("unban时出现异常\n 异常信息 : \n {}".format(e))
        finally:
            session.close()
    else:
        await cmd2.finish("该人/群未被ban插件|{}|".format(name))

