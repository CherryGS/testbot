import asyncio
import pytest
from src.cool import CoolMaker, CoolingError

cool = CoolMaker()


@cool.cool_async(3)
async def func(x):
    return x


class TestCoolMaker:
    @pytest.mark.asyncio
    async def test_async_func(self):
        assert await func(1) == 1
        with pytest.raises(CoolingError):
            await func(1)
        await asyncio.sleep(3)
        assert await func(2) == 2
