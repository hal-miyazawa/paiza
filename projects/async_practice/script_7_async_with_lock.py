# このスクリプトは async with (非同期コンテキストマネージャ) を学びます。
# 共有リソース（ファイル、DB、共有変数など）への同時アクセス制御に活かせます。

import asyncio
import time

async def worker(lock, name, delay):
    # lock を取れたタスクだけがクリティカルセクションに入れる
    # async with は例外時でも lock を解放してくれる
    async with lock:
        print(f"{name} 入室 {time.strftime('%X')}")
        await asyncio.sleep(delay)
        print(f"{name} 退室 {time.strftime('%X')}")

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    lock = asyncio.Lock()

    # 複数タスクが同じリソースを扱う想定
    tasks = [
        asyncio.create_task(worker(lock, "task-1", 2)),
        asyncio.create_task(worker(lock, "task-2", 1)),
        asyncio.create_task(worker(lock, "task-3", 1)),
    ]

    await asyncio.gather(*tasks)
    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
