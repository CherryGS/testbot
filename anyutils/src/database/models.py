from typing import ClassVar, Literal

from pydantic import BaseModel
from sqlalchemy.orm.decl_api import declarative_base
from typing_extensions import Self

from .exception import *

Base = declarative_base()
export_conf = {"exclude_unset": True, "exclude_defaults": False, "exclude_none": True}


class ModelConfig:
    extra: Literal["ignore", "allow", "forbid"] = "ignore"
    orm_mode: bool = True


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
    def check_pk(cls, Model: Base):
        """
        根据传入的 `model` 检查 `pk` 是否相等 , 如果相等将 `pk` 的 `name` 填入类集合]

        Raises:
            `PrimaryKeyNotEqualError`: `pk` 不相等时抛出
        """
        if not cls.__primary_key__:
            cls.__primary_key__ = set()

        for i in cls.schema()["properties"].items():
            try:
                a = i[1]["pk"]
                if a == True:
                    cls.__primary_key__.add(i[0])
            except:
                pass

        s = set()
        d = Model.__dict__
        for i in d:
            if not i.startswith("_") and d[i].primary_key is True:
                s.add(i)

        if s != cls.__primary_key__:
            raise PrimaryKeyNotEqualError("PK 不完全相等")

        cls.__sqla_model__ = Model

    def __hash__(self):
        return hash(tuple(self.dict(include=self.__primary_key__).values()))

    def __eq__(self, other: Self):
        return self.dict(include=self.__primary_key__) == other.dict(
            include=other.__primary_key__
        )

    class Config(ModelConfig):
        pass
