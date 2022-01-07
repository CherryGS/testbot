import asyncio
from typing import Any, Dict, List, Union

import httpx

# from . import ASession, usr
import orjson as js

from exception import *

USER_INFO = "https://codeforces.com/api/user.info?handles={}"
USER_STATUS = "https://codeforces.com/api/user.status?handle={}&from={}&count={}"


async def get_user_info(handle: str) -> Dict:
    """获取用户总体信息

    Args:
        handle (str): 用户名

    Raises:
        QueryError: 查询状态不为 `OK` 时抛出 , 字面为错误原因

    Returns:
        dict: 信息
    """
    url = USER_INFO.format(handle)
    try:
        conn = httpx.AsyncClient()
        res = js.loads((await conn.get(url)).text)
        if res["status"] != "OK":
            raise QueryError(res["comment"])
    except:
        raise
    finally:
        await conn.aclose()
    return res["result"]


async def _get_user_submissions(
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
    url = USER_STATUS.format(handle, f, count)
    try:
        conn = httpx.AsyncClient()
        r = await conn.get(url)
        res = js.loads(r.text)
        while True:
            if res["status"] == "OK":
                break
            elif res["comment"] == "Call limit exceede":
                asyncio.sleep(2)
                r = await conn.get(url)
                print(r)
                res = js.loads(r.text)
            else:
                raise QueryError(res["comment"])
    except:
        raise
    finally:
        await conn.aclose()
    return res["result"]


async def get_user_submissions(
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
        _get_user_submissions(handle, f + i, min(_cnt, count - i))
        for i in range(0, count, _cnt)
    ]
    res = await asyncio.gather(*lis)
    rnt = []
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

    Args:
        lis (List[Any]): [description]
        id (int): [description]

    Returns:
        bool: [description]
    """
    for i in range(len(lis)):
        if lis[i]["id"] == id:
            return i

    return None


async def get_user_submissions_before(handle: str, des_id: int) -> List[Dict[str, Any]]:
    """得到某个 id 之后(时间)的所有提交

    Args:
        handle (str): 用户名
        des_id (int): 指定id

    Returns:
        List[Dict[str, Any]]: 提交列表
    """
    _cnt = 10
    _st = 0
    rnt = []
    while True:
        lis = await get_user_submissions(handle, _st + 1, _cnt)
        s = await _check(lis, des_id)
        if s != None:
            rnt += lis[:s]
            break
        rnt += lis
        _st = _cnt
        _cnt *= 10
    return rnt


if __name__ == "__main__":
    asyncio.run(get_user_submissions_before("paekae", 141863721))

