from functools import cached_property, cache
from typing import Any, List, Optional, Tuple, Union

import colored
from colored import stylize
from PIL import Image as Img
from PIL import ImageFont as ImgFont
from PIL.Image import Image
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont
from pydantic.color import Color

__all__ = [
    "t_colors",
    "t_text",
    "paste_updown",
    "text_colors",
    "ColorString",
]
t_colors = List[Color]
t_text = str


class ColorString:
    def __init__(self, text, color=[Color("#000000")], fmt: bool = True) -> None:
        self.text = self._check_text(text)
        self.color = self._check_color(color)
        if fmt is True:
            self.format()

    @staticmethod
    def _check_text(v):
        return str(v)

    @staticmethod
    def _check_color(v):
        _res = []
        if isinstance(v, Color):
            return [v]
        if isinstance(v, str):
            return [Color(v)]
        for i in v:
            if not isinstance(i, Color):
                i = Color(i)
            _res.append(i)
        return _res

    def format(self):
        """重整颜色使得颜色与字符串长度相等
        
        颜色多则截掉多余的 , 否则补为最后一种颜色
        """
        (self.text, self.color) = self.content

    @cached_property
    def content(self) -> Tuple[t_text, t_colors]:
        """返回重整结果 , 但不应用
        """
        le1 = len(self.text)
        le2 = len(self.color)
        if le1 == le2:
            return (self.text, self.color)

        if le1 < le2:
            color = self.color[:le1]
        else:
            color = self.color + [self.color[-1] for _ in range(le1 - le2)]

        return (self.text, color)

    def __len__(self) -> int:
        """返回字符串长度
        """
        return self.text.__len__()

    def __add__(self, other):
        return ColorString(
            text=(self.text + other.text), color=(self.color + other.color)
        )

    def __str__(self):
        msg = ""
        (txt, col) = self.content
        for i, j in zip(txt, col):
            msg += "({},{})".format(i, j.as_hex())
        return msg

    def print(self, bg: Color = Color("#ffffff")):
        """尝试打印(with color)
        """
        (txt, col) = self.content
        for i, j in zip(txt, col):
            print(stylize(i, colored.fg(j.as_hex()) + colored.bg(bg.as_hex())), end="")
        print()


def paste_updown(img1: Image, img2: Image, loc: Tuple[float, float] = (0, 0)) -> Image:
    """把 img2 贴到 img1 下方 , 如果图片范围超出原图 , 多余部分会由空像素替代

    Args:
        `img1` : [description]
        `img2` : [description]
        `loc` : 左上角位置.
    """
    tmp1 = Img.new(
        "RGBA",
        (
            max(img1.size[0], img2.size[0]) + abs(loc[0]),
            max(img1.size[1], img2.size[1]) + abs(loc[1]),
        ),  # type: ignore
    )
    tmp2 = Img.new(
        "RGBA",
        (
            max(img1.size[0], img2.size[0]) + abs(loc[0]),
            max(img1.size[1], img2.size[1]) + abs(loc[1]),
        ),  # type: ignore
    )
    tmp1.paste(img1, (int((abs(loc[0]) - loc[0]) / 2), int((abs(loc[1]) - loc[1]) / 2)))
    tmp2.paste(img2, (int((abs(loc[0]) + loc[0]) / 2), int((abs(loc[1]) + loc[1]) / 2)))
    final = Img.alpha_composite(tmp2, tmp1)
    max_x = max(
        int((abs(loc[0]) - loc[0]) / 2) + img1.size[0],
        int((abs(loc[0]) + loc[0]) / 2) + img2.size[0],
    )
    max_y = max(
        int((abs(loc[1]) - loc[1]) / 2) + img1.size[1],
        int((abs(loc[1]) + loc[1]) / 2) + img2.size[1],
    )
    return final.crop((0, 0, max_x, max_y))


def text_colors(
    draw: ImageDraw,
    text: ColorString,
    font: Union[Tuple[str, int], FreeTypeFont],
    loc: Tuple[float, float] = (0, 0),
) -> None:
    """绘制一行具有多个颜色的字符串 , (空格占位置不上色)
    Args:
        `draw` : ImageDraw 实例 , 用来绘制的对象
        `text` : `ColorString` 类 , 包含文字和颜色
        `fonttype` : 字体文件
        `fontsize` : 字体大小
        `loc` : 位置. 
        `font` : ImageFont 实例. 
    """

    if isinstance(font, tuple):
        font = ImgFont.truetype(font[0], font[1])
    (t, c) = text.content

    for i in range(len(c) - 1, -1, -1):
        draw.text(loc, t[: i + 1], c[i].as_hex(), font=font)


if __name__ == "__main__":
    tour = ColorString(text="tour", color=["#000000", "#a10703"])
    ist = ColorString(text="ist", color=["#000000"])
    tour.format()
    res = tour + ist
    print(res)
    res.print()
