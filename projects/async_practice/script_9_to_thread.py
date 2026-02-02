# このスクリプトは asyncio.to_thread を学びます。
# ブロッキング処理（時間のかかる同期関数）をスレッドに逃がす時に活かせます。

import asyncio
import time

def blocking_io(name, sec):
    print(f"{name} (同期) 開始 {time.strftime('%X')}")
    time.sleep(sec)
    print(f"{name} (同期) 終了 {time.strftime('%X')}")
    return f"{name} 完了"

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    # to_thread で同期関数を別スレッドで実行する
    results = await asyncio.gather(
        asyncio.to_thread(blocking_io, "job-A", 2),
        asyncio.to_thread(blocking_io, "job-B", 3),
    )

    print("結果:", results)
    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
