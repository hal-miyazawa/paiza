# このスクリプトは async for と async generator を学びます。
# 「一定間隔でデータが流れてくる」ような処理の受け取りに活かせます。

import asyncio
import time

async def ticker(count, interval):
    for i in range(1, count + 1):
        await asyncio.sleep(interval)
        yield f"tick-{i} {time.strftime('%X')}"

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    # async for は async generator から値を受け取るための文法
    async for item in ticker(5, 1):
        print("受信:", item)

    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
