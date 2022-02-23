import re

from nonebot import get_driver, on_message
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from playwright.async_api import async_playwright
