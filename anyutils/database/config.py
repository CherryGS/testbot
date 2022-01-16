from typing import Literal


class ModelConfig:
    extra: Literal["ignore", "allow", "forbid"] = "ignore"
    orm_mode: bool = True
