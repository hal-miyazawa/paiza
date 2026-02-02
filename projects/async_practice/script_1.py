import asyncio
import time

#コルーチン化
async def main():
    print(f"main開始 {time.strftime('%X')}")
    task1 = asyncio.create_task(asyncio.sleep(5))
    task2 = asyncio.create_task(asyncio.sleep(10))
    await task1
    await task2
    print(f"{task1.result()}")
    print(f"{task2.result()}")
    print(f"main終了 {time.strftime('%X')}")



if __name__ == "__main__":
    asyncio.run(main())
