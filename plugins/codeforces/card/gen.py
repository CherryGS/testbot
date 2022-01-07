from typing import Dict
from .utilis import *
import card_config


def month_card_gen(
    card: str, avatar: str, save_path: str, kwargs: Dict[str, Tuple[t_text, t_Colors]],
):
    """画卡

    Args:
        card (str): 卡片基底路径
        avatar (str): 头像文件路径
        save_path (str): 文件存储路径
        kwargs (dict): 请参照卡片配置文件添加参数
    """
    conf = card_config.month_card
    img = Img.open(card)
    img_ava = Img.open(avatar)

    # 把头像放到 card 下面
    final = paste_updown(img, img_ava, conf["img"]["avatar"])

    d = ImgDraw.Draw(final)

    for i in kwargs.keys():
        text_colors(
            d,
            kwargs[i][0],
            conf["text"][i]["font"],
            conf["text"][i]["loca"],
            kwargs[i][1],
        )

    final.save(save_path)


if __name__ == "__main__":
    b = "#000000"
    r = "#ff0a00"
    g = "#4b4b4b"
    colors_seq = make_color_seq([(b, 8), (r, 4), (b, 7), (r, 4), (b, 4)])
    pth = "/home/tickt/project/testbot/plugins/codeforces/card/src/img/card1.png"
    pth_ = "/home/tickt/project/testbot/plugins/codeforces/card/src/img/default_ava.jpg"
    params: Dict[str, Tuple[t_text, t_Colors]] = {
        "handle": ("tourist", [b, r]),
        "rating": ("rating: 3911 (with 3911 max)", colors_seq),
        "accept": ("114", b),
        "submision": ("514", b),
        "max_rate_problem": ("1919", b),
        "contest_parti": ("8", b),
        "virtual_parti": ("10", b),
        "time1": ("2021-01-06", g),
        "time2": ("11:11:11", g),
    }
    month_card_gen(pth, pth_, "test.png", params)
