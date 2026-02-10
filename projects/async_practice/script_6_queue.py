# このスクリプトは asyncio.Queue を使った生産者/消費者モデルを学びます。
# タスク間で安全にデータを受け渡す仕組みとして活かせます。

import asyncio
import time

async def producer(queue):
    for i in range(1, 6):
        await asyncio.sleep(0.5)
        item = f"item-{i}"
        # put は「空きができるまで待つ」可能性があるので await する
        await queue.put(item)
        print(f"produce: {item} {time.strftime('%X')}")

    # 消費者の数だけ終了シグナル(None)を送る
    await queue.put(None)
    await queue.put(None)

async def consumer(queue, name):
    while True:
        # get は「データが来るまで待つ」ので await する
        item = await queue.get()
        try:
            if item is None:
                print(f"{name}: 終了 {time.strftime('%X')}")
                return

            print(f"{name}: 処理開始 {item} {time.strftime('%X')}")
            await asyncio.sleep(1)
            print(f"{name}: 処理完了 {item} {time.strftime('%X')}")
        finally:
            # 1件処理したことをキューに通知 (queue.join と対になる)
            queue.task_done()

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    queue = asyncio.Queue()

    # 複数の消費者を走らせる
    consumers = [
        asyncio.create_task(consumer(queue, "consumer-1")),
        asyncio.create_task(consumer(queue, "consumer-2")),
    ]

    # 生産を開始
    await producer(queue)
    # すべての item が処理されるまで待つ
    await queue.join()

    # 念のため消費者タスクの終了を待つ
    await asyncio.gather(*consumers)

    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
