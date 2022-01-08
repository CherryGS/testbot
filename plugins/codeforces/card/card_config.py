from typing import Any, Dict
from pydantic import BaseSettings


month_card: Dict[Any, Any] = {
    "img": {"avatar": (164, 474),},
    "text": {
        "handle": {"font": ("src/font/SetoFont.ttf", 125), "loca": (157, 109)},
        "rating": {"font": ("src/font/SetoFont.ttf", 50), "loca": (160, 293)},
        "accept": {
            "font": ("src/font/verdana.ttf", 50),
            "loca": (1920 - 969 + 13, 535 - 13),
        },
        "submision": {
            "font": ("src/font/verdana.ttf", 50),
            "loca": (1920 - 849 + 13, 625 - 13),
        },
        "max_rate_problem": {
            "font": ("src/font/verdana.ttf", 50),
            "loca": (1920 - 696 + 13, 708 - 13),
        },
        "contest_parti": {
            "font": ("src/font/verdana.ttf", 50),
            "loca": (1920 - 590 + 13, 799 - 13),
        },
        "max_rating_change": {
            "font": ("src/font/verdana.ttf", 50),
            "loca": (1920 - 672 + 13, 891 - 7),
        },
        "time1": {"font": ("src/font/verdana.ttf", 50), "loca": (160, 816)},
        "time2": {"font": ("src/font/verdana.ttf", 50), "loca": (196, 902)},
    },
}

