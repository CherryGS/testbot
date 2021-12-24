from nonebot.adapters.cqhttp import Bot
from nonebot.adapters.cqhttp import Event
from nonebot.adapters.cqhttp.event import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command, plugins, on_shell_command
from nonebot.log import logger
from nonebot.message import run_preprocessor
from nonebot.plugin import export
from nonebot.typing import T_State
from nonebot import get_driver
from models.admin import plugins_global_control as models
from models import db
from nonebot.exception import FinishedException, IgnoredException
from nonebot.rule import ArgumentParser

driver = get_driver()
conf = driver.config
ban_settings = {0: {}, 1: {}}


@driver.on_startup
async def _():
    # 初始化插件信息
    logger.debug(str(plugins))
    session = db()

    # 加载全局ban
    ban = session.query(models.pluginsBan).all()
    global ban_settings
    for i in ban:
        ban_settings |= {i.ban_type: {i.handle: {i.plugin_name: {}}}}
    session.close()
    logger.info("全局ban初始化成功")

# -----------------------------------------------------------------------------


@run_preprocessor
async def _(matcher: Matcher, bot: Bot, event: Event, state: T_State):
    # ignore掉全局被ban的人/群的matcher
    handle_qq = event.user_id
    name = matcher.plugin_name
    try:
        x = ban_settings[0][handle_qq][name]
        logger.debug("QQ号:{}被全局ban".format(handle_qq))
        raise IgnoredException("QQ号:{}被全局ban".format(handle_qq))
    except KeyError:
        pass
    if isinstance(event, GroupMessageEvent):
        handle_gr = event.group_id
        try:
            x = ban_settings[1][handle_gr][name]
            logger.debug("群号:{}被全局ban".format(handle_gr))
            raise IgnoredException("群号:{}被全局ban".format(handle_gr))
        except KeyError:
            pass
    return

# -----------------------------------------------------------------------------

parser = ArgumentParser()
parser.add_argument('-u')  # 个人 qq 号
parser.add_argument('-g')  # 群号
parser.add_argument('-p')  # 插件名

cmd1 = on_shell_command('ban', parser=parser, permission=SUPERUSER)


@cmd1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # ban 人/群
    args = state['args']
    if isinstance(args, Exception):
        await cmd1.finish("参数填写错误 , 请检查")

    if args.u and args.g:
        await cmd1.finish("个人和群只能选择一个")

    if not args.u and not args.g:
        await cmd1.finish("个人和群必须选择一个")

    session = db()
    if (args.p,) not in session.query(models.pluginsCfg.plugin_name).all():
        await cmd1.finish("参数错误 , |{}| 不在插件列表中".format(args.p))

    ban_type = 0
    handle = None
    name = args.p
    global ban_settings

    if args.g:
        ban_type = 1
        handle = args.g
    else:
        ban_type = 0
        handle = args.u

    handle = int(handle)

    try:
        x = ban_settings[ban_type][handle][name]
        session.close()
    except KeyError:
        try:
            session.add(models.pluginsBan(
                ban_type=ban_type, handle=handle, plugin_name=name))
            session.commit()
            ban_settings |= {ban_type: {handle: {name: {}}}}
        except Exception as e:
            logger.error("向数据库中添加ban时出现异常")
            session.rollback()
            await cmd1.send("向数据库中添加ban时出现异常")
            raise e
        finally:
            session.close()
    print(ban_settings)
    logger.info("ban执行成功")
    await cmd1.finish("ban执行成功")

# -----------------------------------------------------------------------------

parser = ArgumentParser()
parser.add_argument('-u')  # 个人 qq 号
parser.add_argument('-g')  # 群号
parser.add_argument('-p')  # 插件名

cmd2 = on_shell_command('unban', parser=parser, permission=SUPERUSER)


@cmd2.handle()
async def _(bot: Bot, event: Event, state: T_State):
    # unban 人/群
    args = state['args']
    if isinstance(args, Exception):
        await cmd2.finish("参数填写错误 , 请检查")

    if args.u and args.g:
        await cmd2.finish("个人和群只能选择一个")

    if not args.u and not args.g:
        await cmd2.finish("个人和群必须选择一个")

    session = db()

    if (args.p,) not in session.query(models.pluginsCfg.plugin_name).all():
        await cmd2.finish("参数错误 , |{}| 不在插件列表中".format(args.p))

    ban_type = 0
    handle = None
    name = args.p
    global ban_settings

    if args.g:
        ban_type = True
        handle = args.g
    else:
        ban_type = False
        handle = args.u

    try:
        handle = int(handle)
        x = ban_settings[ban_type][handle][name]
        ban_settings[ban_type][handle].pop(name)
        session.query(models.pluginsBan).filter(models.pluginsBan.ban_type == ban_type,
                                                models.pluginsBan.handle == handle, models.pluginsBan.plugin_name == name).delete()
        session.commit()
    except KeyError:
        await cmd2.finish("该人/群未被ban插件|{}|".format(name))
    except Exception as e:
        print(e)
        session.rollback()
        logger.error("unban出现错误 , 信息 {},{},{}".format(ban_type, handle, name))
        await cmd2.finish("unban出现错误")
    finally:
        session.close()

    logger.info("unban执行成功")
    await cmd2.finish("unban执行成功")
