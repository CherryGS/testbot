import asyncio
from httpx import AsyncClient

from playwright.async_api import  Page
from pydantic import BaseModel, validator

from ..exceptions import SourceNotFoundError, UnknownError
from lxml import etree


class Atc(BaseModel, extra="ignore"):
    contest_prefix: str
    contest_id: str
    problem_id: str | None = None

    @validator("contest_prefix")
    def _1(cls, v):
        if v not in ("abc", "arc", "agc"):
            raise ValueError("must be one of 'abc', 'arc', 'agc'")

        return v

    @validator("contest_id")
    def _2(cls, v):
        if len(v) != 3:
            raise ValueError("must len 3")

        if not v.isdigit():
            raise ValueError("must be a number")

        return v

    @validator("problem_id")
    def _3(cls, v):
        if len(v) > 1:
            raise ValueError("must len 1")

        if v not in "abcdefgh" and v is not None:
            raise ValueError("must in 'abcdefgh'")

        return v

    @property
    def p1(self):
        return self.contest_prefix + self.contest_id

    @property
    def p2(self):
        if self.problem_id == None:
            raise ValueError("problem_id is required")
        return self.contest_prefix + self.contest_id + "_" + self.problem_id


def generate_contest_url(data: Atc):
    return f"https://atcoder.jp/contests/{data.p1}"


def generate_problem_url(data: Atc):
    return f"https://atcoder.jp/contests/{data.p1}/tasks/{data.p2}"


def generate_standings_url(data: Atc):
    return generate_contest_url(data) + "/standings"


def generate_editorial_url(data: Atc):
    return generate_contest_url(data) + "/editorial"


async def get_problem_screenshot(string: Atc, page: Page):
    url = generate_problem_url(string)
    await page.goto(url, wait_until="networkidle")
    await page.evaluate(
        "() => { document.getElementById('fixed-server-timer').remove(); }"
    )
    details = page.locator('xpath=//span[@class="lang-en"]//details')
    count = await details.count()
    for i in range(count):
        await details.nth(i).click()
    # ???????????????
    await page.locator("xpath=//a[@class='dropdown-toggle']").evaluate_all(
        "( lis ) => { for(var e of lis) { e.textContent = ''; } }"
    )
    return await page.screenshot(full_page=True, type="jpeg", quality=100)


async def get_contest_screenshot(string: Atc, page: Page):
    url = generate_contest_url(string)
    await page.goto(url)
    await page.evaluate(
        "() => { document.getElementById('fixed-server-timer').remove(); }"
    )
    # ???????????????
    await page.locator("xpath=//a[@class='dropdown-toggle']").evaluate_all(
        "( lis ) => { for(var e of lis) { e.textContent = ''; } }"
    )
    return await page.screenshot(full_page=True, type="jpeg", quality=100)


async def get_standings_screenshot(
    string: Atc, page: Page, username: str, password: str
):
    url = generate_standings_url(string)
    await page.goto(url)

    # ?????????????????????????????????
    name = await page.evaluate("() => { return userScreenName; }")
    if not name:
        # ????????????
        # TODO: Cookie support
        await page.locator("xpath=//input[@id='username']").fill(username)
        await page.locator("xpath=//input[@id='password']").fill(password)
        await page.locator("xpath=//button[@id='submit']").click()
    response = await page.goto(url)
    if not response:
        raise UnknownError("response ??????")

    # ???????????????????????????
    if response.status != 404:
        # ?????? 100 ???
        await page.locator("xpath=//a[text()='100']").click()

    # ???????????????
    await page.locator("xpath=//a[@class='dropdown-toggle']").evaluate_all(
        "( lis ) => { for(var e of lis) { e.textContent = ''; } }"
    )

    # ?????????????????????
    await page.evaluate(
        "() => { document.getElementById('fixed-server-timer').remove(); }"
    )
    return await page.screenshot(full_page=True, type="jpeg", quality=100)


async def get_editorial_screenshot(data: Atc, *, client: AsyncClient, page: Page):
    url = generate_editorial_url(data)
    r = f"//div[@class='col-sm-12']//h3//a[@href='/contests/{data.p1}/tasks/{data.p2}']/../following-sibling::ul[1]/li[1]/a[1]/@href"
    res = etree.HTML((await client.get(url)).content.decode("utf8"), etree.HTMLParser())
    res = res.xpath(r)
    if not res:
        # * ?????????????????????????????? 'Overall editorial'
        # TODO: ?????????
        raise SourceNotFoundError("??????????????????????????? , ????????????????????????????????????")
    res = res[0]  # type: ignore
    await page.goto(f"https://atcoder.jp{res}")

    # ?????????????????????
    await page.evaluate(
        "() => { document.getElementById('fixed-server-timer').remove(); }"
    )
    # ???????????????
    await page.locator("xpath=//a[@class='dropdown-toggle']").evaluate_all(
        "( lis ) => { for(var e of lis) { e.textContent = ''; } }"
    )
    return await page.screenshot(full_page=True, type="jpeg", quality=100)
