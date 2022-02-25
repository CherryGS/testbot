from nonebot import _driver

if _driver is None:
    raise Exception("该插件必须要在所有调用其的插件之前启动")

from .admin import *

# from .controller import *
