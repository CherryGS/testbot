import httpx
import asyncio
import time

async def _user_submission_(user_name: str, start_idx: int = 1, end_idx: int = 100, freq: int = 2) -> list:
    """
    说明
        获得某个用户的提交列表

    返回
        一个 ``list`` 代表提交记录

    参数
        ``user_name``: 用户名(长度大于2)
        ``start_idx``: 以从后往前数第几个提交作为起点,默认 1
        ``end_idx`` : 请求多少个提交,默认 100
        ``freq``: 请求频率(秒)，最少为 2 (CF的api要求)
    
    """
    freq = max(freq, 2)
    await asyncio.sleep(freq)
    __url = r"https://codeforces.com/api/user.status?handle={}&from={}&count={}".format(user_name, start_idx, end_idx)
    __res_dic : dict
    async with httpx.AsyncClient() as client :
        __res = await client.get(__url)
        __res_dic = __res.json()

    if __res_dic['status'] == 'OK' :
        return __res_dic['result']
    else :
        raise Exception("{}".format(__res_dic['comment']))
    
    
async def get_solved_by_day(handle: str, day_lim : int = 30, is_sol: bool = 1) -> tuple:
    """
    说明
        返回用户在指定天数内的提交（通过）次数

    返回
        ``(bool, str)`` : 是否查询成功，值（或错误输出）

    参数
        ``handle``  : 用户名(大于2)
        ``day_lim`` : 日期之内的 AC (提交)数，以发送请求时为准
        ``is_sol``  : 是否只返回通过次数，默认为是
    """
    _res : list
    _tim : int
    cnt = 100 # 初始查询提交次数
    while True:
        if cnt > 10000:
            return (0, "此人提交次数太多了 , 太强了以至于查不到结果!")
        print(cnt, "--------------")
        try:
            _res = await _user_submission_(handle, 1, cnt)
        except Exception as e:
            return (0, repr(e)) # 返回打包的错误信息供展示
        for i in _res[::-1]:
            if 'creationTimeSeconds' in i:
                _tim = i['creationTimeSeconds']
                break
            else :
                _tim = time.time()
        now_tim = time.time()
        delta = (now_tim-_tim)/3600/24
        if delta >= day_lim :
            break
        else :
            cnt *= 10

    _sum = 0 # 统计AC（提交次数）
    for i in _res:
        if 'creationTimeSeconds' not in i:
            continue
        _tim = i['creationTimeSeconds']
        now_tim = time.time()
        delta = (now_tim-_tim)/3600/24 # 相差时间
        if delta >= day_lim:
            break
        if i['verdict'] != 'OK':
            if is_sol != 1:
                _sum += 1
        else :
            _sum += 1
    return (1, _sum)