# このスクリプトは タイムアウト と キャンセル の基本を学びます。
# 遅すぎる処理の打ち切りや、不要になった処理の停止に活かせます。

import asyncio
import time

# 学びメモ
# create_task → タスクを作って今すぐ走らせる。待たない。
# gather → 複数のコルーチン/タスクをまとめて待って、結果を集める。

async def slow_task(name, sec):
    try:
        print(f"{name} 開始 {time.strftime('%X')}")
        # 長い待ち時間を想定した処理
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
    # 内部では対象タスクにキャンセルを送ります。

    # await wait_for(...)
    #     └─内部タスクが動く
    #         └─timeout → CancelledError が内部に入る
    #             └─内部で後処理 (except/finally)
    #     └─外側に TimeoutError

    try:
        await asyncio.wait_for(slow_task("timeout-demo", 5), timeout=2)
    except asyncio.TimeoutError:
        print("timeout-demo はタイムアウトしました")

    # create_task で起動したタスクは cancel で中断できます。
    # cancel だけでは止まらないので、await してキャンセル処理を完了させる
    task = asyncio.create_task(slow_task("cancel-demo", 5))
    # create_task したら動き出す
# 　→ await を付けなくても「実行は開始される」

# await しないと「待たない＆結果も受け取らない」
# 　→ ただし task.result() で後から受け取ることは可能
# 　→ そもそもイベントループが止まると途中で終わってしまう
    await asyncio.sleep(1)
    task.cancel()
    # task.cancel() した時点では 「キャンセルを要求しただけ」で、
    # 実際に止まったかどうかは確定してないんです。
    # だから await task
    try:
        await task
    except asyncio.CancelledError:
        print("cancel-demo のキャンセルを確認")

    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
