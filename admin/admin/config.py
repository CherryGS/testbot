from pydantic import BaseSettings, Extra

__all__ = ["AdminConfig"]


class AdminConfig(BaseSettings, extra=Extra.ignore):
    reply_group_id: int
