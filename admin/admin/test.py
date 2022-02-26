from .locker import *
from .sender import *
from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.exception import NoneBotException
import asyncio

test = on_command("testadmin", permission=SUPERUSER)

sender_ = Sender(sender.group_id)


@test.handle()
@sender.catch(RuntimeError, matcher=test)
async def _():
    raise RuntimeError("test catch")


@locker.lock("1")
async def sleep(t):

    await asyncio.sleep(t)


async def sleep_(t):
    locker.set_lock()
    await asyncio.sleep(t)
    locker.rm_lock()


@test.handle()
@sender.catch(LockedError, log="冷却中...")
async def _():
    await asyncio.gather(sleep(5), sleep(5))


@test.handle()
@sender.catch(LockedError, func_msg=lambda x: str(x))
async def _():
    await asyncio.gather(sleep_(5), sleep_(5))


@test.handle()
@sender_.catch(NoneBotException, log="test need_raise")
@sender.catch(Exception)
async def _():
    raise NoneBotException
