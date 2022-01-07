import asyncio
from typing import Any, Dict, List, Union

import httpx
import orjson as js
from nonebot.log import logger

from .exception import *


__all__ = [
    "get_user_info",
    "get_submissions",
    "get_submissions_before",
    "get_submissions_days",
    "get_submissions_days_from",
]

_USER_INFO = "https://codeforces.com/api/user.info?handles={}"
_USER_STATUS = "https://codeforces.com/api/user.status?handle={}&from={}&count={}"

async def get_user_info(handle: str) -> Dict:
    """获取用户总体信息

    Args:
        handle (str): 用户名

    Raises:
        QueryError: 查询状态不为 `OK` 时抛出 , 字面为错误原因

    Returns:
        dict: 信息
    """
    url = _USER_INFO.format(handle)
    try:
        # TODO : 代理改掉
        conn = httpx.AsyncClient(proxies="http://192.168.137.1:7777")
        res = js.loads((await conn.get(url)).text)
        if res["status"] != "OK":
            raise QueryError(res["comment"])
    except:
        raise
    finally:
        await conn.aclose()
    return res["result"][0]


async def _get_submissions(
    handle: str, f: int = 1, count: int = 1
) -> List[Dict[str, Any]]:
    """获取用户提交信息

    Args:
        handle (str): 用户名
        f (int, optional): 从第几个提交开始( 1 为第 1 个). Defaults to 1.
        count (int, optional): 获取几个提交. Defaults to 1.

    Raises:
        QueryError: 查询状态不为 `OK` 时抛出 , 字面为错误原因

    Returns:
        List[Dict[str, Any]]: 提交信息
    """
    url = _USER_STATUS.format(handle, f, count)

    try:
        # TODO : 代理改掉
        conn = httpx.AsyncClient(proxies="http://192.168.137.1:7777")

        try:
            r = await conn.get(url)
            res = js.loads(r.text)
        except Exception as e:
            logger.opt(exception=e).error(str(r.text))
            raise

        while True:
            if res["status"] == "OK":
                break
            elif res["comment"] == "Call limit exceede":
                asyncio.sleep(2)
                r = await conn.get(url)
                res = js.loads(r.text)
            else:
                raise QueryError(res["comment"])

    except:
        raise

    finally:
        await conn.aclose()

    return res["result"]


async def get_submissions(
    handle: str, f: int = 1, count: int = 1
) -> List[Dict[str, Any]]:
    """获取用户提交信息

    Args:
        handle (str): 用户名
        f (int, optional): 从第几个提交开始( 1 为第 1 个). Defaults to 1.
        count (int, optional): 获取几个提交. Defaults to 1.

    Raises:
        QueryError: 查询状态不为 `OK` 时抛出 , 字面为错误原因

    Returns:
        List[Dict[str, Any]]: 提交信息
    """
    _cnt = int(count / 2) + 1

    # 并行
    lis = [
        _get_submissions(handle, f + i, min(_cnt, count - i))
        for i in range(0, count, _cnt)
    ]
    rnt = []
    res = await asyncio.gather(*lis)
    for i in res:
        rnt += i

    # 串行
    # rnt = []
    # for i in range(0, count, _cnt):
    #     asyncio.sleep(1)
    #     rnt += _get_user_submissions(handle, f + i, min(_cnt, count - i))

    return rnt


async def _check(lis: List[Any], id: int) -> Union[int, None]:
    """检查给定提交 id 是否在给定提交列表里 , 如果有返回编号 , 如果没有返回 `None`
    编号要求从大到小

    Args:
        lis (List[Any]): [description]
        id (int): [description]

    Returns:
        bool: [description]
    """
    if lis[0]["id"] < id or lis[-1]["id"] > id:
        return None

    # TODO : 换用二分(虽然不会快多少)
    for i in range(len(lis)):
        if lis[i]["id"] == id:
            return i

    return None


async def _get_cnt(
    handle: str, des_id: int, force: bool = False, l: int = 1, r: int = 10000000
) -> int:
    async def _check(mid):
        nonlocal des_id, handle
        r = await _get_submissions(handle, mid, 1)
        return r[0]["id"] <= des_id if len(r) > 0 else 1

    if force:
        # 二分
        while l < r:
            mid = l + ((r - l) >> 1)
            if await _check(mid):
                r = mid
            else:
                l = mid + 1
        return r
    else:
        # 倍增
        _cnt = 1
        while True:
            res = await _get_submissions(handle, _cnt, 1)
            if (len(res) > 0 and res[0]["id"] <= des_id) or len(res) == 0:
                return _cnt >> 3
            _cnt <<= 3


async def get_submissions_before(
    handle: str, des_id: int, force: bool = False
) -> List[Dict[str, Any]]:
    """得到某个 id 之后(时间,不包含)的所有提交 , 因为可能正在提交 , 所以 `rnt` 中可能有重复数据

    Args:
        `handle (str)`: 用户名
        `des_id (int)`: 指定id
        `force (bool)`: 指定是否启用二分方法 (由于网络IO , 除非要找 `vjudge1` 这种 , 否则尽量不要启用)

    Returns:
        `List[Dict[str, Any]]`: 提交列表
    """
    rnt = []
    if not force:
        # 倍增法
        _cnt = 10
        _st = 0
        while True:
            lis = await get_submissions(handle, _st + 1, _cnt)
            s = await _check(lis, des_id)
            if s != None:
                rnt += lis[:s]
                break
            rnt += lis
            _st = _cnt
            if _cnt < 10000:
                _cnt *= 10
            else:
                _cnt += 10000
    else:
        # 二分法
        des = await _get_cnt(handle, des_id, True)
        rnt = await get_submissions(handle, 1, des + 10)
    return rnt


async def get_submissions_days(
    handle: str, now: int, days: int = 30, force: bool = False
) -> List[Dict[str, Any]]:
    """获得数天的记录

    Args:
        handle (str): 用户名
        now (int): 现在时间
        days (int, optional): 天数. Defaults to 30.
        force (bool, optional): 是否启用二分方法. Defaults to False.

    Returns:
        List[Dict[str, Any]]: ..
    """
    # TODO : 二分
    _cnt = 1
    rnt = []

    while True:
        res = await _get_submissions(handle, _cnt, 1)
        if not res or ((now - res[0]["creationTimeSeconds"]) / 3600 / 24 >= days):
            k = await get_submissions(handle, 1, _cnt)

            for i in k:
                if i["creationTimeSeconds"] >= now and (
                    (now - i["creationTimeSeconds"]) / 3600 / 24 <= days
                ):
                    rnt.append(i)
            break

        _cnt <<= 3
    return rnt


async def get_submissions_days_from(
    handle: str, des_id: int, now: int, days: int = 30, force: bool = False
) -> List[Dict[str, Any]]:
    """获得数天内从某次提交开始(不包含)的记录

    Args:
        handle (str): 用户名
        des_id (int): 定位的提交编号
        now (int): 现在时间
        days (int, optional): 天数. Defaults to 30.
        force (bool, optional): 是否启用二分方法. Defaults to False.

    Returns:
        List[Dict[str, Any]]: ..
    """
    # TODO : 二分
    _cnt = 1
    rnt = []
    cnt = await _get_cnt(handle, des_id, force)

    while True:
        res = await _get_submissions(handle, _cnt, 1)
        if not res or ((now - res[0]["creationTimeSeconds"]) / 3600 / 24 >= days):
            k = await get_submissions(handle, cnt - 10, _cnt - cnt + 10)

            for i in k:
                if i["id"] < des_id:
                    if i["creationTimeSeconds"] >= now and (
                        (now - i["creationTimeSeconds"]) / 3600 / 24 <= days
                    ):
                        rnt.append(i)
            break

        _cnt <<= 3
    return rnt


if __name__ == "__main__":
    print(asyncio.run(get_submissions_before("paekae", 137348285)))

