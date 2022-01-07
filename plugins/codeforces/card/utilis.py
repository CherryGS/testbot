from typing import List, Tuple, Union

from PIL import Image as Img
from PIL import ImageDraw as ImgDraw
from PIL import ImageFont as ImgFont
from PIL.Image import Image
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont

t_Colors = Union[str, List[str]]
t_text = str


def paste_updown(img1: Image, img2: Image, loc: Tuple[float, float] = (0, 0)) -> Image:
    """把 img2 贴到 img1 下方 , 如果图片范围超出原图 , 多余部分会由空像素替代

    Args:
        img1 (Image): [description]
        img2 (Image): [description]
        loc (Tuple[float, float], optional): 左上角位置. Defaults to (0, 0).
    """
    tmp1 = Img.new(
        "RGBA",
        (
            max(img1.size[0], img2.size[0]) + abs(loc[0]),
            max(img1.size[1], img2.size[1]) + abs(loc[1]),
        ),
    )
    tmp2 = Img.new(
        "RGBA",
        (
            max(img1.size[0], img2.size[0]) + abs(loc[0]),
            max(img1.size[1], img2.size[1]) + abs(loc[1]),
        ),
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
    text: str,
    font: Union[Tuple[str, int], FreeTypeFont],
    loc: Tuple[float, float] = (0, 0),
    colors: t_Colors = "#000000",
) -> None:
    """绘制一行具有多个颜色的字符串 , (空格占位置不上色)

    Args:
        draw (ImageDraw): ImageDraw 实例 , 用来绘制的对象
        text (str): 文字
        fonttype (str): 字体文件
        fontsize (int): 字体大小
        loc (Tuple[float, float], optional): 位置. 
        colors (Union[List[str], str], optional): 颜色字符串(列表) , 如果为字符串则只绘制一种颜色 , 否则按照列表一对一绘制颜色 , 如果长度小于文字长度多余部分会绘制最后一种颜色. 
        font (ImageFont, optional): ImageFont 实例. 
    """
    if isinstance(font, tuple):
        font = ImgFont.truetype(font[0], font[1])
    if isinstance(colors, str):
        draw.text(loc, text, colors, font=font)
    else:
        le1 = len(colors)
        le2 = len(text)
        if le1 < le2:
            draw.text(loc, text, colors[-1], font=font)
            le1 -= 1
        k = range(min(le1, le2) - 1, -1, -1)
        for i in k:
            draw.text(loc, text[: i + 1], colors[i], font=font)


def make_color_seq(lis: List[Tuple[str, int]]) -> List[str]:
    """输入压缩序列 , 输出展开后的序列
    
    例如 [("#000000", 2), ] 会得到 ["#000000", "#000000", ]
    """
    res = []
    for i in lis:
        res += [i[0] for j in range(i[1])]
    return res

