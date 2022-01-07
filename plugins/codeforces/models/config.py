from typing import Optional
from pydantic import BaseSettings
from . import AsyncEngine


class DBSettings(BaseSettings):

    plugin_codeforces_db: str = ""
    AEngine: Optional[AsyncEngine] = None
    debug: bool

    class Config:
        extra = "ignore"

