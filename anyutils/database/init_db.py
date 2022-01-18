from dataclasses import dataclass
from typing import Any, Dict, Set

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine


@dataclass
class DBCfg:
    name: str
    link: str
    debug: bool = False

    def __eq__(self, __o) -> bool:

        return self.name == __o.name

    def __hash__(self) -> int:
        return hash(self.name)


class RegEngine:
    _Engine: Dict[str, AsyncEngine]
    _link: Set[DBCfg]
    _used: Set[DBCfg]

    def __init__(self, doc: str = "Default") -> None:
        self.__doc__ = doc
        self._Engine = dict()
        self._link = set()
        self._used = set()

    def add(self, name: str, link: str, debug: bool = False, dupli: bool = True):
        """
        添加一个待初始化的引擎信息

        Args:
            `name` : 识别名
            `link` : 数据库链接
            `debug` : echo 是否开启
            `dupli` : 是否允许重复(重复忽略)

        Raises:
            `KeyError`: 重复时抛出
        """
        r = DBCfg(name=name, link=link, debug=debug)
        if r in self._link or r in self._used:
            msg = "引擎信息 {} 已经存在".format(name)
            if dupli:
                logger.warning(msg)
            else:
                raise KeyError(msg)
        else:
            self._link.add(r)
            msg = "引擎信息添加成功({})".format(",".join([name, link, str(debug)]))
            logger.info(msg)

    def init(self):
        """
        根据初始化信息初始化引擎 (重复跳过)
        """
        while self._link:
            r = self._link.pop()
            if r.name in self._Engine:
                logger.warning("尝试初始化的引擎 {} 已经存在 , 忽略".format(r.name))
                continue
            self._used.add(r)
            self._Engine[r.name] = create_async_engine(
                r.link,
                pool_recycle=3600,
                echo=r.debug,
                future=True,
            )
            msg = "引擎 {} 成功初始化".format(r.name)
            logger.debug(msg)

    def get(self, name: str) -> AsyncEngine:
        """
        根据引擎识别名获得引擎

        Args:
            `name` : 识别名

        Raises:
            `TypeError`: 识别名存在但类型不为 `AsyncEngine` 时抛出
            `KeyError`: 识别名不存在时抛出

        Returns:
            `AsyncEngine`
        """
        if self._link:
            self.init()

        if not isinstance(self._Engine[name], AsyncEngine):
            raise TypeError("类型不为 AsyncEngine , 可能由于初始化出错")

        try:
            return self._Engine[name]
        except KeyError:
            raise KeyError("没有名为 {} 的引擎".format(name))

    def add_one(self, name: str, engine: AsyncEngine, dupli: bool = True):
        """
        添加一个已经初始化了的引擎

        Args:
            `name` : 识别名
            `engine` : 引擎实例
            `dupli` : 是否允许重复(忽略行为)

        Raises:
            `KeyError`: 重复时抛出
        """
        if name in self._Engine:
            msg = "引擎 {} 已经存在".format(name)
            if dupli:
                logger.warning(msg)
            else:
                raise KeyError(msg)
        else:
            msg = "成功添加引擎 {}".format(name)
            self._Engine[name] = engine
            logger.info(msg)

    def from_cfg(self, dic: Dict[str, Any], dupli: bool = True):
        """
        从配置字典中加载引擎实例

        Args:
            `dic` : 配置字典
            `dupli` : 是否允许重复
        """
        for i in dic.items():
            if isinstance(i[1], AsyncEngine):
                self.add_one(i[0], i[1], dupli)


reg = RegEngine()
