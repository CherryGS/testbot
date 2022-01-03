import asyncio
import time


async def func1():
    time.sleep(10)
    print("1")


async def func2():
    print(2)


async def main():
    await func1()
    await func2()


asyncio.run(main())
