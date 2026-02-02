# このスクリプトは 同時実行数の制限 (セマフォ) を学びます。
# リクエストの集中を避けたり、外部サービスに負荷をかけ過ぎない制御に活かせます。

import asyncio
import time

async def limited_work(sem, name, sec):
    # セマフォを使って同時実行数を制限する
    async with sem:
        print(f"{name} 開始 {time.strftime('%X')}")
        await asyncio.sleep(sec)
        print(f"{name} 終了 {time.strftime('%X')}")
        return f"{name} 完了"

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    sem = asyncio.Semaphore(3)  # 同時に3つまで
    durations = [1, 2, 1, 3, 2, 1, 2, 1]

    tasks = [
        asyncio.create_task(limited_work(sem, f"task-{i+1}", sec))
        for i, sec in enumerate(durations)
    ]

    results = await asyncio.gather(*tasks)
    print("結果:", results)

    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
