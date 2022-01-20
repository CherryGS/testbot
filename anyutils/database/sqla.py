from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Literal, Set

from loguru import logger
from pydantic import BaseModel, PrivateAttr
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm.decl_api import declarative_base
from typing_extensions import Self

Base = declarative_base()
export_conf = {"exclude_unset": True, "exclude_defaults": False, "exclude_none": True}


class ModelConfig:
    extra: Literal["ignore", "allow", "forbid"] = "ignore"
    orm_mode: bool = True


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

    def __init__(
        self, doc: str = "Default", lim: List[str] = ["sqlite", "postgresql"]
    ) -> None:
        self.__doc__ = doc
        self._Engine = dict()
        self._link = set()
        self._used = set()
        self.lim = lim

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
            if self._Engine[r.name].dialect.name not in self.lim:
                raise TypeError("暂不支持该数据库")
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
            if engine.dialect.name not in self.lim:
                raise TypeError("暂不支持该数据库")
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


class BsModel(BaseModel):
    __primary_key__: ClassVar[set[str]] = set()
    __sqla_model__: ClassVar[Base]

    @classmethod
    def make_value(cls, stmt, ign=set(), all: set | None = None) -> dict:
        """
        为 sqla 插入时 pk 重复时使用 on_conflict_update 更新定制

        Args:
            `stmt` : sqla 语句
            `ign` : 忽视的列名 , 优先级高于允许
            `all` : 允许的列名 , 优先级低于忽视 , 如果为默认值则选取所有

        Raises:
            `TypeError`: 忽视的列名中有不存在的时抛出

        Returns:
            `Dict`: `set_` 处使用的 `dict`
        """
        for i in ign:
            if i not in cls.__sqla_model__.__dict__:
                raise TypeError(f"忽视的列名{i}不存在!")
        if all:
            for i in all:
                if i not in cls.__sqla_model__.__dict__:
                    raise TypeError(f"需要的列名{i}不存在!")
        r = dict()
        d = cls.__dict__["__fields__"].keys() if all is None else all
        for i in d:
            if i not in cls.__primary_key__ and i not in ign:
                r[i] = eval(f"stmt.excluded.{i}")
        return r

    @classmethod
    def check_pk(cls, Model: Base) -> bool:
        """
        根据传入的 `model` 检查 `pk` 是否相等 , 如果相等将 `pk` 的 `name` 填入类集合

        Args:
            `Model` : [description]

        Raises:
            `TypeError`: `pk` 不相等时抛出

        Returns:
            `bool`: 如果执行了检查 , 返回 `True` 否则返回 `False`
        """
        cls.__sqla_model__ = Model
        if cls.__primary_key__:
            return False
        else:
            cls.__primary_key__ = set()
        for i in cls.schema()["properties"].items():
            try:
                a = i[1]["pk"]
                if a == True:
                    cls.__primary_key__.add(i[0])
            except:
                print(i)
                pass
        s = set()
        d = Model.__dict__
        for i in d:
            if not i.startswith("_") and d[i].primary_key is True:
                s.add(i)
        if s != cls.__primary_key__:
            raise TypeError("PK 不完全相等")

        return True

    def __hash__(self):
        return hash(tuple(self.dict(include=self.__primary_key__).values()))

    def __eq__(self, other: Self):
        return (
            self.dict(include=self.__primary_key__).values()
            == other.dict(include=other.__primary_key__).values()
        )

    class Config(ModelConfig):
        pass


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
