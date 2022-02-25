import sys
import asyncio
from codeforces import method as ts


def test_main():
    async def main(i):
        data = [
            "BucketPotato",
            "Vercingetorix",
            "jiangly",
            "s7win99",
            "user202729_",
            "carlszk",
            "mukim",
            "Mohamed2209",
        ]
        with open(f"./tmp/img/{i}.png", "wb") as f:
            f.write(await ts.get_spstandings_screenshot(data, 103492))

    for i in range(1, 2):
        asyncio.run(main(i))
