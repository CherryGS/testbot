from typing import List, Optional
from pydantic import BaseSettings
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry
from sqlalchemy.orm.session import sessionmaker

__all__: List[str] = []


class DBSettings(BaseSettings):

    db_link: str = ""
    debug: bool = False
    AEngine: Optional[AsyncEngine] = None

    class Config:
        extra = "ignore"


_mapper_registry = registry()


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True

    # these are supplied by the sqlalchemy2-stubs, so may be omitted
    # when they are installed
    registry = _mapper_registry
    metadata = _mapper_registry.metadata

    __init__ = _mapper_registry.constructor
