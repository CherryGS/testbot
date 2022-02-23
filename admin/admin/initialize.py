import os

import yaml

from .config import AdminConfig

__all__ = ["cfg"]

pth: str

if not os.path.isfile("Admin_Config.yml"):
    if not os.path.isfile("Admin_Config.yaml"):
        raise FileNotFoundError("插件Admin配置文件未找到")
    else:
        pth = "Admin_Config.yaml"
else:
    pth = "Admin_Config.yml"

with open(pth, "r", encoding="utf8") as f:
    cfg = AdminConfig(**yaml.safe_load(f.read()))
