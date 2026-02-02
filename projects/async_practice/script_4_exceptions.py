# このスクリプトは 例外が起きたときの asyncio.gather の挙動を学びます。
# 並行処理のどれかが失敗した場合にどう扱うかの判断に活かせます。

import asyncio
import time

async def sometimes_fail(name, sec, fail=False):
    print(f"{name} 開始 {time.strftime('%X')}")
    await asyncio.sleep(sec)
    if fail:
        raise ValueError(f"{name} でエラーが発生")
    print(f"{name} 完了 {time.strftime('%X')}")
    return f"{name} OK"

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    # return_exceptions=False (デフォルト) だと、例外が出た時点で例外が伝播します。
    try:
        await asyncio.gather(
            sometimes_fail("task-A", 1),
            sometimes_fail("task-B", 2, fail=True),
            sometimes_fail("task-C", 3),
        )
    except Exception as e:
        print("例外を捕捉:", repr(e))

    # return_exceptions=True にすると、例外も結果として返ります。
    results = await asyncio.gather(
        sometimes_fail("task-D", 1),
        sometimes_fail("task-E", 2, fail=True),
        return_exceptions=True,
    )

    for r in results:
        if isinstance(r, Exception):
            print("例外結果:", repr(r))
        else:
            print("正常結果:", r)

    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
