from anyutils.hook import HookMaker
import pytest


def func_sync_add(x, y):
    # 同步函数
    return x + y


def func_sync_gen(x):
    # 同步生成器函数
    for i in range(x):
        yield x


async def func_async_add(x, y):
    # 协程函数
    return x + y


async def func_async_gen(x):
    # 异步生成器函数
    for i in range(x):
        yield i


coro = func_async_add(1, 2)  # 协程
gen = func_sync_gen(10)  # 同步生成器
agen = func_async_gen(10)  # 异步生成器

data = {func_sync_add, func_sync_gen, func_async_add, func_async_gen, coro, gen, agen}


@pytest.fixture(scope="module")
def hook():
    return HookMaker()


class TestHookMaker:
    @pytest.mark.parametrize("func", [func_async_add])
    def test_add_async_func(self, hook: HookMaker, func):
        hook.add_async_func(func)

    @pytest.mark.parametrize(
        "func", [func_sync_add, func_sync_gen, func_async_gen, coro, gen, agen]
    )
    def test_add_async_func_raise(self, hook: HookMaker, func):
        with pytest.raises(TypeError):
            hook.add_async_func(func)

    @pytest.mark.parametrize("func", [func_sync_add])
    def test_add_sync_func(self, hook: HookMaker, func):
        hook.add_sync_func(func)

    @pytest.mark.parametrize(
        "func", [func_async_add, func_sync_gen, func_async_gen, coro, gen, agen]
    )
    def test_add_sync_func_raise(self, hook: HookMaker, func):
        with pytest.raises(TypeError):
            hook.add_sync_func(func)

    @pytest.mark.parametrize("func", [coro])
    def test_add_coro(self, hook: HookMaker, func):
        hook.add_coro(func)

    @pytest.mark.parametrize(
        "func",
        [func_async_add, func_sync_gen, func_async_gen, func_sync_add, gen, agen],
    )
    def test_add_coro_raise(self, hook: HookMaker, func):
        with pytest.raises(TypeError):
            hook.add_coro(func)

    def test_run_sync_func(self, hook: HookMaker):
        res = hook.run_sync_func(1, 2)
        assert res[0] == 3

    @pytest.mark.asyncio
    async def test_run_async_func(self, hook: HookMaker):
        res = await hook.run_async_func(1, 2)
        assert res[0] == 3

    @pytest.mark.asyncio
    async def test_run_coro(self, hook: HookMaker):
        res = await hook.run_coro()
        assert res[0] == 3

    @pytest.mark.asyncio
    async def test_run_hook(self, hook: HookMaker):
        hook._hooked_coro.clear()
        res = await hook.run_hook(1, 2)
        assert res == ([3], [], [3])

    def test_run_sync_func_raise(self, hook: HookMaker):
        with pytest.raises(Exception):
            hook.run_sync_func(1, 2, 3)

    @pytest.mark.asyncio
    async def test_run_async_func_raise(self, hook: HookMaker):
        with pytest.raises(Exception):
            await hook.run_async_func(1, 2, 3)

    @pytest.mark.asyncio
    async def test_run_coro_raise(self, hook: HookMaker):
        hook.add_coro(coro)
        with pytest.raises(Exception):
            await hook.run_coro()

    @pytest.mark.asyncio
    async def test_run_hook_raise(self, hook: HookMaker):
        with pytest.raises(Exception):
            await hook.run_hook(1, 2, 3)
