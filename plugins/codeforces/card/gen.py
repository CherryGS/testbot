from typing import Dict, Optional, Union
from .utilis import *
from PIL import Image as Img
from PIL import ImageDraw as ImgDraw
from .card_config import *

__all__ = ["month_card_gen"]


def month_card_gen(
    card: Union[str, bytes],
    avatar: Union[str, bytes],
    card_conf: Dict[str, Any],
    save_path: Optional[str] = None,
) -> Union[None, bytes]:
    """画卡

    Args:
        card (str): 卡片基底路径
        avatar (str): 头像文件路径
        save_path (str): 文件存储路径
        kwargs (dict): 请参照卡片配置文件添加参数
    """
    card_conf = month_card
    img = Img.open(card)
    img_ava = Img.open(avatar)

    # 把头像放到 card 下面
    final = paste_updown(img, img_ava, card_conf["img"]["avatar"])

    d = ImgDraw.Draw(final)

    for i in card_conf.keys():
        text_colors(
            d,
            card_conf[i][0],
            card_conf["text"][i]["font"],
            card_conf["text"][i]["loca"],
            card_conf[i][1],
        )
    if save_path != None:
        final.save(save_path)
    else:
        return final.tobytes()


if __name__ == "__main__":
    b = "#000000"
    r = "#ff0a00"
    g = "#4b4b4b"
    colors_seq = make_color_seq([(b, 8), (r, 4), (b, 7), (r, 4), (b, 4)])
    pth = "/home/tickt/project/testbot/plugins/codeforces/card/src/img/card1.png"
    pth_ = "/home/tickt/project/testbot/plugins/codeforces/card/src/img/default_ava.jpg"
    # params: Dict[str, Tuple[t_text, t_colors]] = {
    #     "handle": ("tourist", [b, r]),
    #     "rating": ("rating: 3911 (with 3911 max)", colors_seq),
    #     "accept": ("114", b),
    #     "submision": ("514", b),
    #     "max_rate_problem": ("1919", b),
    #     "contest_parti": ("8", b),
    #     "max_rating_change": ("-50", g),
    #     "time1": ("2021-01-06", g),
    #     "time2": ("11:11:11", g),
    # }
    # month_card_gen(pth, pth_, "test.png", params)
