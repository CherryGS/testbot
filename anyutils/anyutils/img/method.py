from PIL import Image as Img
from PIL import ImageFont as ImgFont
from PIL.Image import Image
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont
from .schema import ColorString


def paste_down(
    img1: Image,
    img2: Image,
    loc: tuple[int, int] = (0, 0),
    bg: tuple[int, int, int] | None = None,
) -> Image:
    """把 img2 贴到 img1 下方 , 如果图片范围超出原图 , 多余部分会由透明像素替代

    Args:
        `loc` : `img2` 左上角相对 `img1` 左上角的位置. (右下正)
        `bg` : 背景颜色 , 默认为透明
    """
    tmp = Img.new(
        "RGBA",
        (
            -min(0, loc[0]) + max(img1.size[0], img2.size[0] + loc[0]),
            -min(0, loc[1]) + max(img1.size[1], img2.size[1] + loc[1]),
        ),
        bg if bg != None else (0, 0, 0, 0),
    )
    tmp.paste(img2, (max(0, loc[0]), max(0, loc[1])))
    tmp.paste(img1, (min(0, loc[0]), min(0, loc[1])))
    return tmp
    # 根据图片最大可能大小创建两幅临时图层
    siz = (
        max(img1.size[0], img2.size[0]) + abs(int(loc[0])),
        max(img1.size[1], img2.size[1]) + abs(int(loc[1])),
    )
    tmp1 = Img.new("RGBA", siz)
    tmp2 = Img.new("RGBA", siz)
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


def draw_text(
    draw: ImageDraw,
    text: ColorString,
    font: tuple[str, int] | FreeTypeFont,
    loc: tuple[float, float] = (0, 0),
) -> None:
    """绘制一行具有多个颜色的字符串 , (空格占位置不上色)
    Args:
        `draw` : `ImageDraw 实例` , 用来绘制的对象
        `text` : `ColorString` 类 , 包含文字和颜色
        `loc` : 位置 , 左上角.
        `font` : `ImageFont 实例`或构造实例所需的`文件路径+字号`.
    """

    if isinstance(font, tuple):
        font = ImgFont.truetype(font[0], font[1])
    (t, c) = text.content

    for i in range(len(c) - 1, -1, -1):
        draw.text(loc, t[: i + 1], c[i].as_hex(), font=font)
