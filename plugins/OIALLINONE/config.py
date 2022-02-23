from pydantic import BaseSettings, Extra


class ATCConfig(BaseSettings, extra=Extra.ignore):
    username: str
    password: str


class Config(BaseSettings, extra=Extra.ignore):
    atcoder: ATCConfig
