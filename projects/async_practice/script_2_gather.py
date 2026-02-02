# このスクリプトは asyncio.gather を使って複数の非同期処理を並行に実行し、
# まとめて結果を受け取る方法を学びます。
# ネットワークアクセスや複数のAPI呼び出しなど、待ち時間が多い処理の集約に活かせます。

import asyncio
import time

async def work(name, sec):
    print(f"{name} 開始 {time.strftime('%X')}")
    await asyncio.sleep(sec)
    print(f"{name} 終了 {time.strftime('%X')}")
    return f"{name} 完了({sec}秒)"

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    # gather は複数のコルーチンを同時進行させ、結果をリストで返します。
    results = await asyncio.gather(
        work("task-A", 2),
        work("task-B", 1),
        work("task-C", 3),
    )

    print("結果:", results)
    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
