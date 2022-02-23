import asyncio

from playwright.async_api import Browser, Page
from pydantic import BaseModel, ValidationError, validator

from .exceptions import UnknownError


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
    await page.goto(url)
    await page.evaluate(
        "() => { document.getElementById('fixed-server-timer').remove(); }"
    )
    details = page.locator('xpath=//span[@class="lang-en"]//details')
    count = await details.count()
    for i in range(count):
        await details.nth(i).click()
    return await page.screenshot(full_page=True, type="jpeg", quality=100)


async def get_contest_screenshot(string: Atc, page: Page):
    url = generate_contest_url(string)
    await page.goto(url)
    await page.evaluate(
        "() => { document.getElementById('fixed-server-timer').remove(); }"
    )
    return await page.screenshot(full_page=True, type="jpeg", quality=100)


async def get_standings_screenshot(
    string: Atc, page: Page, username: str, password: str
):
    url = generate_standings_url(string)
    await page.goto(url)

    # 登录名保存在网页源码里
    name = await page.evaluate("() => { return userScreenName; }")
    if not name:
        # 手动登录
        # TODO: Cookie support
        await page.locator("xpath=//input[@id='username']").fill(username)
        await page.locator("xpath=//input[@id='password']").fill(password)
        await page.locator("xpath=//button[@id='submit']").click()
    response = await page.goto(url)
    if not response:
        raise UnknownError("response 为空")

    # 判断该比赛是否存在
    if response.status != 404:
        # 选择 100 人
        await page.locator("xpath=//a[text()='100']").click()

    # 隐藏用户名
    await page.locator(
        "xpath=//a[@class='dropdown-toggle']", has_text=username
    ).evaluate_all("( lis ) => { for(var e of lis) { e.textContent = ''; } }")

    # 删除右下角时间
    await page.evaluate(
        "() => { document.getElementById('fixed-server-timer').remove(); }"
    )
    return await page.screenshot(full_page=True, type="jpeg", quality=100)


async def get_editorial_screenshot(data: Atc, page: Page):
    url = generate_editorial_url(data)
    r = f"//div[@class='col-sm-12']//h3//a[@href='/contests/{data.p1}/tasks/{data.p2}']/../following-sibling::ul[1]/li[1]/a[1]"
    await page.goto(url)
    res = await page.get_attribute(f"xpath={r}", "href", strict=True)
    print(f"https://atcoder.jp{res}")
    await page.goto(f"https://atcoder.jp{res}")

    # 删除右下角时间
    await page.evaluate(
        "() => { document.getElementById('fixed-server-timer').remove(); }"
    )
    return await page.screenshot(full_page=True, type="jpeg", quality=100)


if __name__ == "__main__":
    import asyncio

    from playwright.async_api import async_playwright

    async def main():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            res = await get_editorial_screenshot(
                Atc(contest_prefix="arc", contest_id="113", problem_id="c"), page
            )
            with open("test.jpeg", "wb") as f:
                f.write(res)
            await browser.close()

    asyncio.run(main())
    # r = requests.get("https://atcoder.jp/contests/arc313/standings")
    # print(r.status_code)
