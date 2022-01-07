from pydantic import BaseSettings


class DBSettings(BaseSettings):

    plugin_codeforces_db: str = ""
    debug: bool

    class Config:
        extra = "ignore"

