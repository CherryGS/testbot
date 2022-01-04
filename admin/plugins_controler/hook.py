from typing import Any, Callable, Set
import asyncio
from nonebot.log import logger


class Hook(object):
    _init_db_complete_hook: Set[Callable[..., Any]] = set()

    def add_hook(self, func):
        self._init_db_complete_hook.add(func)
        return func

    async def run_hook(self):
        if self._init_db_complete_hook:
            try:
                lis = list(map(lambda x: x(), self._init_db_complete_hook))
                await asyncio.gather(*lis)
            except Exception as e:
                logger.opt(exception=e).error("执行插件数据库初始化后 HOOK 时出错")


hook = Hook()
