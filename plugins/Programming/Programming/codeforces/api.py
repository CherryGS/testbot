from enum import Enum
from typing import Generic, Literal, TypeVar

from httpx import AsyncClient
from pydantic import BaseModel
from pydantic.generics import GenericModel

from .schema import Contest, User, Problem, RanklistRow

officialBaseUrl = "https://codeforces.com/api/"
unofficialBaseUrl = "https://codeforces.com/"

T = TypeVar("T")
strBoolean = Literal["true", "false"]


class Status(str, Enum):
    OK = "OK"
    FAILED = "FAILED"


class UserResponse(BaseModel):
    status: Status
    comment: str | None = None
    result: list[User] | None = None


class CListResponse(BaseModel):
    status: Status
    comment: str | None = None
    result: list[Contest] | None = None


class SubStandingResponse(BaseModel):
    contest: Contest
    problems: list[Problem]
    rows: list[RanklistRow]


class StandingResponse(BaseModel):
    status: Status
    comment: str | None = None
    result: SubStandingResponse | None = None


async def get_user_info(handles: str, *, client: AsyncClient):
    url = officialBaseUrl + "/user.info/" + f"?handles={handles}"
    return UserResponse.parse_raw((await client.get(url)).content)


async def get_contest_list(gym: strBoolean = "false", *, client: AsyncClient):
    url = officialBaseUrl + "/contest.list" + f"?gym={gym}"
    return CListResponse.parse_raw((await client.get(url)).content)


async def get_contest_standings(
    contestId: int,
    handles: str,
    from_: int = 1,
    count: int = 100,
    room: int | Literal[""] = "",
    showUnofficial: strBoolean = "true",
    *,
    client: AsyncClient,
):
    url = (
        officialBaseUrl
        + "/contest.standings"
        + f"?contestId={contestId}"
        + f"&handles={handles}"
        + f"&from={from_}"
        + f"&count={count}"
        + f"&room={room}"
        + f"&showUnofficial={showUnofficial}"
    )
    print(url)
    return StandingResponse.parse_raw((await client.get(url)).content)


def get_contest_page_url(contestId: int):
    if contestId < 100000:
        return unofficialBaseUrl + f"/contest/{contestId}"
    else:
        return unofficialBaseUrl + f"/gym/{contestId}"


def get_ctstandings_page_url(contestId: int, num: int):
    if contestId < 100000:
        return unofficialBaseUrl + f"/contest/{contestId}/standings/page/{num}"
    else:
        return unofficialBaseUrl + f"/gym/{contestId}/standings/page/{num}"


async def get_contest_page(*, contestId: int, num: int = 1, client: AsyncClient):
    return (
        await client.get(get_ctstandings_page_url(contestId=contestId, num=num))
    ).content


def get_problem_page_url(contestId: int, idx: str):
    if contestId < 100000:
        return unofficialBaseUrl + f"/contest/{contestId}/problem/{idx}"
    else:
        return unofficialBaseUrl + f"/gym/{contestId}/problem/{idx}"
