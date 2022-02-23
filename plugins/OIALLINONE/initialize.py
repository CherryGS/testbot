import os

import yaml

from .config import Config

__all__ = ["cfg"]

pth: str

if not os.path.isfile("Plugins_Config.yml"):
    if not os.path.isfile("Plugins_Config.yaml"):
        raise FileNotFoundError("插件Admin配置文件未找到")
    else:
        pth = "Plugins_Config.yaml"
else:
    pth = "Plugins_Config.yml"

with open(pth, "r", encoding="utf8") as f:
    cfg = Config(**yaml.safe_load(f.read()))
