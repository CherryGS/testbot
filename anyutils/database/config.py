from typing import Literal

export_conf = {"exclude_unset": True, "exclude_defaults": False, "exclude_none": True}


class ModelConfig:
    extra: Literal["ignore", "allow", "forbid"] = "forbid"
    orm_mode: bool = True
