import os
from pydantic import ValidationError

import yaml
import nonebot

from .config import AdminConfig

__all__ = ["cfg"]

try:
    cfg = AdminConfig(**nonebot.get_driver().config.dict())
except ValidationError:
    raise
