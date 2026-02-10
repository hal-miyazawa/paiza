# このスクリプトは asyncio.gather を使って複数の非同期処理を並行に実行し、
# まとめて結果を受け取る方法を学びます。
# ネットワークアクセスや複数のAPI呼び出しなど、待ち時間が多い処理の集約に活かせます。

import asyncio
import time

async def work(name, sec):
    # '%X' は strftime の書式指定子で（環境の言語・地域設定）に応じた時刻の表現
    # 非同期関数内でも普通に print や return ができる
    print(f"{name} 開始 {time.strftime('%X')}")
    # ここが「待ち時間のある処理」の代わり
    await asyncio.sleep(sec)
    print(f"{name} 終了 {time.strftime('%X')}")
    return f"{name} 完了({sec}秒)"

async def main():

    print(f"main 開始 {time.strftime('%X')}")

    # gather は複数のコルーチンを同時進行させ、結果をリストで返します。
    # 返る順序は「渡した順番」と同じ (完了順ではない)
    results = await asyncio.gather(
        work("task-A", 2),
        work("task-B", 1),
        work("task-C", 3),
    )

    print("結果:", results)
    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
