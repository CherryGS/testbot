from functools import cached_property

import colored
from colored import stylize
from pydantic.color import Color


class ColorString:
    def __init__(
        self, text: str, color: list[Color | str] = [Color("#000000")], fmt: bool = True
    ) -> None:
        """
        初始化一个带颜色的字符串
        """
        self.text = text
        self.color = self._check_color(color)
        if fmt is True:
            self.format()

    @staticmethod
    def _check_color(v):
        if isinstance(v, Color):
            return [v]
        if isinstance(v, str):
            return [Color(v)]

        _res = []
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
    def content(self) -> tuple[str, list[Color]]:
        """返回重整结果 , 但不应用"""
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
        """返回字符串长度"""
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
        """尝试打印(with color)"""
        (txt, col) = self.content
        for i, j in zip(txt, col):
            print(stylize(i, colored.fg(j.as_hex()) + colored.bg(bg.as_hex())), end="")
        print()
