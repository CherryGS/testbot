COMMAND_LOCK = "_command_lock"

from pydantic import BaseSettings, Extra


class Config(BaseSettings, extra=Extra.ignore):
    atcoder_user: str | None = None
    atcoder_pswd: str | None = None
