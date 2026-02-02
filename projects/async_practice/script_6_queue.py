# このスクリプトは asyncio.Queue を使った生産者/消費者モデルを学びます。
# タスク間で安全にデータを受け渡す仕組みとして活かせます。

import asyncio
import time

async def producer(queue):
    for i in range(1, 6):
        await asyncio.sleep(0.5)
        item = f"item-{i}"
        await queue.put(item)
        print(f"produce: {item} {time.strftime('%X')}")

    # 消費者の数だけ終了シグナル(None)を送る
    await queue.put(None)
    await queue.put(None)

async def consumer(queue, name):
    while True:
        item = await queue.get()
        try:
            if item is None:
                print(f"{name}: 終了 {time.strftime('%X')}")
                return

            print(f"{name}: 処理開始 {item} {time.strftime('%X')}")
            await asyncio.sleep(1)
            print(f"{name}: 処理完了 {item} {time.strftime('%X')}")
        finally:
            queue.task_done()

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    queue = asyncio.Queue()

    consumers = [
        asyncio.create_task(consumer(queue, "consumer-1")),
        asyncio.create_task(consumer(queue, "consumer-2")),
    ]

    await producer(queue)
    await queue.join()

    # 念のため消費者タスクの終了を待つ
    await asyncio.gather(*consumers)

    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
