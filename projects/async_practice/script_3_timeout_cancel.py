# このスクリプトは タイムアウト と キャンセル の基本を学びます。
# 遅すぎる処理の打ち切りや、不要になった処理の停止に活かせます。

import asyncio
import time

async def slow_task(name, sec):
    try:
        print(f"{name} 開始 {time.strftime('%X')}")
        await asyncio.sleep(sec)
        print(f"{name} 完了 {time.strftime('%X')}")
        return f"{name} 完了"
    except asyncio.CancelledError:
        # キャンセルされたときの後処理を書く場所
        print(f"{name} はキャンセルされました {time.strftime('%X')}")
        raise

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    # wait_for は指定時間を超えると TimeoutError を投げます。
    try:
        await asyncio.wait_for(slow_task("timeout-demo", 5), timeout=2)
    except asyncio.TimeoutError:
        print("timeout-demo はタイムアウトしました")

    # create_task で起動したタスクは cancel で中断できます。
    task = asyncio.create_task(slow_task("cancel-demo", 5))
    await asyncio.sleep(1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("cancel-demo のキャンセルを確認")

    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
