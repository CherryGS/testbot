#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# nonebot.load_builtin_plugins("single_session")
nonebot.load_builtin_plugins("echo")

# Please DO NOT modify this file unless you know what you are doing!
# As an alternative, you should use command `nb` or modify `pyproject.toml` to load plugins
nonebot.load_from_toml("pyproject.toml")

# nonebot.load_plugin("admin.test")
nonebot.load_plugin("admin.nonebot_plugin_PCtrl")

# Modify some config / config depends on loaded configs
#
# config = driver.config
# do something...


if __name__ == "__main__":
    nonebot.run(app="__mp_main__:app")
