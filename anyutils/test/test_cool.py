import asyncio

import pytest
from anyutils.cool import CoolingError, CoolMaker


cool = CoolMaker()


@cool.cool_async(3)
async def func(x):
    return x


class TestCoolMaker:
    async def test_async_func(self):
        assert await func(1) == 1
        with pytest.raises(CoolingError):
            await func(1)
        await asyncio.sleep(3)
        assert await func(2) == 2
