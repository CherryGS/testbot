import asyncio
import time
from itertools import count

import orjson
from anyutils import DOMTree as dt
from httpx import AsyncClient
from lxml import etree
from playwright.async_api import Page, async_playwright

from .schema import *
from .api import *


def ratingColor(rating: int | None):
    if rating == None:
        return "lack"
    if rating >= 3000:
        return "legendary"
    elif rating >= 2600:
        return "red"
    elif rating >= 2100:
        return "orange"
    elif rating >= 1900:
        return "violet"
    elif rating >= 1600:
        return "blue"
    elif rating >= 1400:
        return "cyan"
    elif rating >= 1200:
        return "green"
    elif rating >= 0:
        return "gray"


def time_format(t: int):
    r = ":" + ("0" + str((t // 60) % 60))[-2:]
    r = ("0" + str((t // 3600) % 24))[-2:] + r
    if t >= 3600 * 24:
        r = ("0" + str(((t // 3600) // 24)))[-2:] + ":" + r
    return r


def generate_line(
    data: RanklistRow,
    even: bool,
    contest: Contest,
    problems: list[Problem],
    ratings: list[int | None],
    has_penalty: bool,
    has_hack: bool,
):
    # some useful vari
    dark = "dark" if not even else ""

    # 0 body
    body = dt("tr").add_props("participantid", ["1"])

    # 1 rank column
    # 赛时参加显示 rank , 赛后不显示
    rank = dt("td").add_props("class", [dark, "left"])
    if data.rank != 0:
        # 赛后参加时 rank 不为 0
        rank.text = data.rank
    body.add(rank)

    # 2 Who column
    # 名字一列框架
    who = (
        dt("td")
        .add_props("class", [dark, "contestant-cell"])
        .add_props("style", ["text-align:left;padding-left:1em;"])
    )

    ## TODO: 2.1 country img
    # 国旗
    # ! 该功能需要再次访问个人信息 , 暂不实装
    # img = dt("img")
    # img.props._class = ElementProp('class', {'standings-flag'})
    # img.props.src = ElementProp('src', {f'http://codeforces.com/{}'})

    ## TODO: 2.2 contestant's time
    pass

    ## 2.3 star
    # 判断是否是打星
    if data.party.participantType == data.party.participantType.OUT_OF_COMPETITION:
        # 分数超过限制
        star = dt("small", "*")
        who.add(star)
    elif data.party.participantType == data.party.participantType.PRACTICE:
        # 赛后 非vp
        star = dt("span", " * ")
        who.add(star)

    ## 2.4 username
    # 枚举成员
    tmp_lis = []
    for i in zip(data.party.members, ratings):
        col = ratingColor(i[1])
        name = (
            dt("a")
            .add_props("href", ["http://"])
            .add_props("class", ["rated-user", f"user-{col}"])
        )
        # 给名字上颜色
        if col == "legendary":
            fl = dt("span", i[0].handle[0]).add_props(
                "class", ["legendary-user-first-letter"]
            )
            name.text = f"{i[0].handle[1:]}"
            name.add(fl)
        else:
            name.text = i[0].handle

        tmp_lis.append(name)

    if data.party.teamName != None:
        tm = dt("span").add_props("style", ["font-size: 1.1rem;"])
        tm.add(dt("a", data.party.teamName).add_props("href", ["http://"]))
        tm.add(dt("span", ":"))
        le = len(tmp_lis)
        for i in tmp_lis:
            tm.add(i)
            if le > 1:
                tm.add(dt("span", ","))
            le -= 1
        who.add(tm)
    else:
        for i in tmp_lis:
            who.add(i)

    ## 2.5 vp
    if data.party.participantType == data.party.participantType.VIRTUAL:
        vp = dt("sup").add_props("style", ["margin-left: 0.25em;font-size: 8px;"])
        ### 2.5.1 sharp
        sharp = dt("a", "#").add_props("href", ["http://"])
        vp.add(sharp)

        who.add(vp)

    body.add(who)

    # 3 points
    # 分数
    pts = dt("td").add_props("class", [dark])
    if (
        data.points
        and data.party.participantType != data.party.participantType.PRACTICE
    ):
        # 如果分数不为 0 或者不是赛后非 vp 则不显示时间
        pts.text = data.points
    body.add(pts)

    # 4 penalty
    # ICPC 罚时
    if has_penalty:
        pn = dt("td").add_props("class", [dark])
        if data.penalty < 10000 and data.penalty:
            pn.text = data.penalty
        body.add(pn)

    # 5 hack
    if has_hack:
        hack = (
            dt("td").add_props("style", ["font-size: 9px;"]).add_props("class", [dark])
        )
        s_hack = dt("span", f"+{data.successfulHackCount}").add_props(
            "class", ["successfulChallengeCount"]
        )
        u_hack = dt("span", f"-{data.unsuccessfulHackCount}").add_props(
            "class", ["unsuccessfulChallengeCount"]
        )

        # hack 数字渲染
        if data.successfulHackCount and data.unsuccessfulHackCount:
            # * 这里冒号之间不能使用空格 , 否则无法正确渲染间距
            hack.add(s_hack).add("span", "&nbsp;:&nbsp;").add(u_hack)
        elif data.successfulHackCount:
            hack.add(s_hack)
        elif data.unsuccessfulHackCount:
            hack.add(u_hack)

        body.add(hack)

    # 6 problems
    for i in data.problemResults:
        bd = dt("td").add_props("class", [dark])

        ## 6.1 is pass ?
        ### 6.1.1 pass
        # * cell-accepted 是ICPC赛制赛后的属性值 , cell-passed-system-test 是赛时的属性值或者CF赛制赛后属性值
        ps = dt("span")
        if contest.type == contest.type.ICPC:
            ps.add_props("class", ["cell-accepted"])
        else:
            ps.add_props("class", ["cell-passed-system-test"])

        if i.points == 1:
            if i.rejectedAttemptCount:
                ps.text = "+" + str(i.rejectedAttemptCount)
            else:
                ps.text = "+"
        else:
            ps.text = int(i.points)

        tm = dt("span")
        if (
            i.bestSubmissionTimeSeconds != None
            and data.party.participantType != data.party.participantType.PRACTICE
        ):
            tm.add_props("class", ["cell-time"])
            tm.text = f"{time_format(i.bestSubmissionTimeSeconds)}"

        ### 6.1.2 unsubmit
        us = dt("span").add_props("class", ["cell-unsubmitted"])

        ### 6.1.3 reject
        rj = dt("span", f"-{i.rejectedAttemptCount}").add_props(
            "class", ["cell-rejected"]
        )

        if i.points != 0:
            bd.add(ps)
            if i.bestSubmissionTimeSeconds != None:
                bd.add(tm)
        elif i.rejectedAttemptCount != 0:
            bd.add(rj)
        else:
            bd.add(us)

        body.add(bd)

    return body


async def get_standings_screenshot(contestId: int, num: int, *, page: Page):
    await page.goto(get_contest_page_url(contestId=contestId, num=num))
    return await page.screenshot(type="png", full_page=True)


async def get_spstandings_screenshot(
    data: list[str],
    contestId: int,
    showUnofficial: strBoolean = "true",
    *,
    client: AsyncClient,
    page: Page,
):
    # ! 注意 , 因为颜色直接查找现在的 rating 获得 , 所以和 cf 原榜单不一定一样
    ratings_lis: list[list[int | None]] = []
    tree = etree.HTML(
        await get_contest_page(contestId=contestId, client=client),
        etree.HTMLParser(),
    )
    has_penalty = len(tree.xpath("//table//*[contains(text(), 'Penalty')]")) == 1
    has_hack = len(tree.xpath("//table//*[@title='Hacks']")) == 1
    res = await get_contest_standings(
        contestId, ";".join(data), showUnofficial=showUnofficial, client=client
    )

    if res.status != res.status.OK:
        raise ValueError(res.comment)

    assert res.result is not None, "出现了一些意料之外的错误..."

    for i in res.result.rows:
        users = await get_user_info(
            ";".join([j.handle for j in i.party.members]), client=client
        )
        if users.status != users.status.OK:
            raise ValueError(users.comment)

        assert users.result is not None

        ratings_lis.append([j.rating for j in users.result])
        # * 延迟
        await asyncio.sleep(1)

    # 赛后参加 rank 为 0 , 放到最后 , 其余排序 (Python默认从大到小)
    s = sorted(
        zip(res.result.rows, ratings_lis),
        key=lambda x: -x[0].rank if x[0].rank else -1000000,
    )
    lines = []

    # 用来判别第一个是否该染黑 (最底下的那一列是黑的)
    col_switch = bool((len(ratings_lis) & 1) ^ 1)
    for i, j, k in zip([tt[0] for tt in s], count(0), [tt[1] for tt in s]):
        lines.append(
            generate_line(
                i,
                bool(j & 1) ^ col_switch,
                res.result.contest,
                res.result.problems,
                k,
                has_penalty,
                has_hack,
            ).output()
        )
        # # TODO: DEBUG ONLY
        # with open(f"tmp/html/{j}.html", "w") as f:
        #     f.write(lines[-1])

    # async with async_playwright() as dri:
    #     browser = await dri.chromium.launch(
    #         headless=False, proxy={"server": "http://127.0.0.1:7777"}
    #     )
    #     ctx = await browser.new_context(
    #         # viewport={"width": 2560, "height": 1440},
    #         device_scale_factor=2,
    #     )
    #     page = await ctx.new_page()

    await page.goto(
        get_contest_page_url(contestId=contestId, num=1), wait_until="load"
    )

    # 移除已有的列
    await page.locator(
        "xpath=//table[@class='standings']//tr[@participantid]"
    ).evaluate_all("( list ) => { for (let e of list) { e.remove(); } } ")

    # 将获取的列添加进表格
    await page.locator("xpath=//table[@class='standings']//tr[1]").evaluate(
        "( e , list ) => { for (let r of list) { e.insertAdjacentHTML('afterend', r); } }",
        lines,
    )
    return await page.screenshot(type="png", full_page=True)


async def get_problem_screenshot(contestId: int, idx: str, *, page: Page):
    await page.goto(get_problem_page_url(contestId, idx), wait_until="networkidle")
    return await page.screenshot(type="png", full_page=True)


if __name__ == "__main__":
    import asyncio
    import sys

    async def main(i):
        data = [
            "BucketPotato",
            "Vercingetorix",
            "jiangly",
            "s7win99",
            "user202729_",
            "carlszk",
            "mukim",
            "Mohamed2209",
        ]
        # with open(f"./tmp/img/{i}.png", "wb") as f:
        #     f.write(await get_spstandings_screenshot(data, 103492))

    for i in range(1, 2):
        asyncio.run(main(i))
