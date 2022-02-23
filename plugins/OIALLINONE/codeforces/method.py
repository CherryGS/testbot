import asyncio

import orjson
from httpx import AsyncClient
from playwright.async_api import Page, async_playwright

from schema import *
from anyutils import DOMTree as dt, ElementProp
import time


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class Result(BaseModel):
    contest: Contest
    problems: list[Problem]
    rows: list[RanklistRow]


class Standings(BaseModel):
    status: str
    result: Result

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Users(BaseModel):
    status: str
    result: list[User]


def ratingColor(rating: int):
    if rating >= 3000:
        return "legendary"
    elif rating >= 2600:
        return "red"
    elif rating >= 2100:
        return "orange"
    elif rating >= 1900:
        return "purple"
    elif rating >= 1600:
        return "blue"
    elif rating >= 1400:
        return "cyan"
    elif rating >= 1200:
        return "green"
    elif rating >= 0:
        return "gray"
    else:
        return "lack"


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
    ratings: list[int],
):
    # some useful vari
    dark = "dark" if not even else ""

    # 0 body
    body = dt("tr").add_props("participantid", {"1"})

    # 1 rank column
    rank = dt("td", data.rank).add_props("class", {dark, "left"})
    body.add(rank)

    # 2 Who column
    who = (
        dt("td")
        .add_props("class", {dark, "contestant-cell"})
        .add_props("style", {"text-align:left;padding-left:1em;"})
    )

    ## TODO: 2.1 country img
    ## ! 该功能需要再次访问个人信息 , 暂不实装
    # img = dt("img")
    # img.props._class = ElementProp('class', {'standings-flag'})
    # img.props.src = ElementProp('src', {f'http://codeforces.com/{}'})

    ## TODO: 2.2 contestant's time
    pass

    ## 2.3 out rating
    if data.party.participantType == data.party.participantType.OUT_OF_COMPETITION:
        otr = dt("small", "*")
        who.add(otr)

    ## 2.4 username
    tmp_lis = []
    for i in zip(data.party.members, ratings):
        col = ratingColor(i[1])
        name = (
            dt("a")
            .add_props("href", {"http://"})
            .add_props("class", {"rated-user", f"user-{col}"})
        )
        if col == "legendary":
            fl = dt("span", i[0].handle[0]).add_props(
                "class", {"legendary-user-first-letter"}
            )
            name.text = f"{i[0].handle[1:]}"
            name.add(fl)
        else:
            name.text = i[0].handle

        tmp_lis.append(name)

    if data.party.teamName != None:
        tm = dt("span").add_props("style", {"font-size: 1.1rem;"})
        tm.add(dt("a", data.party.teamName).add_props("href", {"http://"}))
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
        vp = dt("sup").add_props("style", {"margin-left: 0.25em;font-size: 8px;"})
        ### 2.5.1 sharp
        sharp = dt("a", "#").add_props("href", {"http://"})
        vp.add(sharp)

        who.add(vp)

    body.add(who)

    # 3 points
    pts = dt("td").add_props("class", {dark})
    ptsa = dt("span", data.points).add_props("style", {"font-weight:bold;"})
    pts.add(ptsa)

    body.add(pts)

    # 4 penalty
    if contest.type == contest.type.ICPC and data.penalty is not None:
        pn = dt("td").add_props("class", {dark})
        if data.penalty < 10000:
            pn.text = data.penalty
        body.add(pn)

    # 5 hack
    # TODO: Finish
    if not contest.type == contest.type.ICPC:
        hack = (
            dt("td").add_props("style", {"font-size: 9px;"}).add_props("class", {dark})
        )

        body.add(hack)

    # 6 problems
    for i in data.problemResults:
        bd = dt("td").add_props("class", {dark})

        ## 6.1 is pass ?
        ### 6.1.1 pass
        ps = dt("span").add_props("class", {"cell-passed-system-test"})
        if i.points == 1:
            if i.rejectedAttemptCount:
                ps.text = "+" + str(i.rejectedAttemptCount)
            else:
                ps.text = "+"
        else:
            ps.text = str(i.points)

        tm = dt("span")
        if i.bestSubmissionTimeSeconds != None:
            tm.add_props("class", {"cell-time"})
            tm.text = f"{time_format(i.bestSubmissionTimeSeconds)}"

        ### 6.1.2 unsubmit
        us = dt("span").add_props("class", {"cell-unsubmitted"})

        ### 6.1.3 reject
        rj = dt("span", f"{i.rejectedAttemptCount}").add_props(
            "class", {"cell-rejected"}
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


async def get_spstandings_screenshot(
    data: list[str], contest_id: int, showUnofficial: str = "true"
):
    url1 = f"http://codeforces.com/api/contest.standings?contestId={contest_id}&showUnofficial={showUnofficial}&handles={';'.join(data)}"
    url2 = f"https://codeforces.com/contest/{contest_id}/standings/page/1"
    url3 = "https://codeforces.com/api/user.info?handles={}"
    ratings_lis = []
    async with AsyncClient() as client:
        res = Standings.parse_raw((await client.get(url1)).content)
        for i in res.result.rows:
            users = Users.parse_raw(
                (
                    await client.get(
                        url3.format(":".join([j.handle for j in i.party.members]))
                    )
                ).content
            )
            ratings_lis.append([j.rating for j in users.result])
    s = sorted(
        zip(res.result.rows, ratings_lis),
        key=lambda x: -x[0].rank if x[0].rank else -1000000,
    )
    lines = []
    for i, j, k in zip([tt[0] for tt in s], range(100), [tt[1] for tt in s]):
        lines.append(
            generate_line(
                i, bool(j ^ 1), res.result.contest, res.result.problems, k
            ).output()
        )
        # TODO: DEBUG ONLY
        with open(f"tmp/{j}.html", "w") as f:
            f.write(lines[-1])

    async with async_playwright() as dri:
        browser = await dri.chromium.launch(
            headless=False, proxy={"server": "http://127.0.0.1:7777"}
        )
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(url2)

        # 移除底部跳转链接 , 美化
        await page.locator("xpath=//div[@class='custom-links-pagination']").evaluate(
            "( e ) => { e.remove(); }"
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
        return await page.screenshot(quality=100, type="jpeg")


if __name__ == "__main__":
    import asyncio

    async def main(i):
        data = ["jiangly", "heltion", "s7win99", "Vercingetorix", "peti1234"]
        with open(f"./sd/{i}.jpeg", "wb") as f:
            f.write(await get_spstandings_screenshot(data, 1644))
        await asyncio.sleep(10)

    for i in range(1, 100):
        asyncio.run(main(i))
