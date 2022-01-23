from dataclasses import dataclass
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy import Column
from .exception import *


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
    _Engine: dict[str, AsyncEngine]
    _link: set[DBCfg]
    _used: set[DBCfg]

    def __init__(
        self, doc: str = "Default", lim: list[str] = ["sqlite", "postgresql"]
    ) -> None:
        self.__doc__ = doc
        self._Engine = dict()
        self._link = set()
        self._used = set()
        self.lim = lim

    def add(self, name: str, link: str, debug: bool = False):
        """
        添加一个待初始化的引擎信息

        Args:
            `name` : 唯一识别名
            `link` : 数据库链接
            `debug` : echo 是否开启

        Raises:
            `DuplicateEngineError`: 重复时抛出
        """
        r = DBCfg(name=name, link=link, debug=debug)
        if r in self._link or r in self._used:
            msg = f"引擎信息 {name} 已经存在"
            raise DuplicateEngineError(msg)
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
                raise DuplicateEngineError(f"引擎信息 {r.name} 已经存在")
            self._used.add(r)
            self._Engine[r.name] = create_async_engine(
                r.link,
                pool_recycle=3600,
                echo=r.debug,
                future=True,
            )
            if self._Engine[r.name].dialect.name not in self.lim:
                raise NotSupportedDatabaseError(
                    f"暂不支持数据库{self._Engine[r.name].dialect.name}"
                )
            msg = "引擎 {} 成功初始化".format(r.name)
            logger.debug(msg)

    def get(self, name: str) -> AsyncEngine:
        """
        根据引擎识别名获得引擎

        Args:
            `name` : 识别名
        """
        if self._link:
            self.init()

        try:
            if not isinstance(self._Engine[name], AsyncEngine):
                raise TypeError("类型不为 AsyncEngine , 可能由于初始化出错")
            return self._Engine[name]
        except KeyError:
            raise NotFoundEngineError("没有名为 {} 的引擎".format(name))

    def add_one(self, name: str, engine: AsyncEngine):
        """
        添加一个已经初始化了的引擎

        Args:
            `name` : 识别名
            `engine` : 引擎实例
            `dupli` : 是否允许重复(忽略行为)

        """
        if name in self._Engine:
            msg = "引擎 {} 已经存在".format(name)
            raise DuplicateEngineError(msg)
        else:
            if engine.dialect.name not in self.lim:
                raise NotSupportedDatabaseError(f"暂不支持该数据库{engine.dialect.name}")
            self._Engine[name] = engine
            msg = "成功添加引擎 {}".format(name)
            logger.info(msg)


def anywhere(stmt, data: set[tuple[Column[Any], Any]]):
    """
    将值非 `None` 的语句用 `where` 拼接上

    比如 `data = ((User.id, 2), (User.name, None))` 会被配成

    `stmt = stmt.where(User.id==2)`
    """
    for i in data:
        if i[1] is not None:
            stmt = stmt.where(i[0] == i[1])
    return stmt


def anywhere_lim(stmt, data: set[tuple[Column[Any], Any]], lim: int | None = None):
    if lim != None and lim != len(data):
        raise KeyError(f"len(data)={len(data)} and lim={lim}")
    return anywhere(stmt, data)
