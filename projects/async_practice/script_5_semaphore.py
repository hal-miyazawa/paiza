# このスクリプトは 同時実行数の制限 (セマフォ) を学びます。
# リクエストの集中を避けたり、外部サービスに負荷をかけ過ぎない制御に活かせます。
import asyncio
import time


# tasks で「行ってこい」の指示を一斉に出す
# limited_work 入口で「同時3名まで」
# 全員終わったら results に集合

async def limited_work(sem, name, sec):
    # セマフォを使って同時実行数を制限する
    # async with を抜けると自動でセマフォが解放される
    # 4つ目以降のタスクは「入れない」のではなく「ここで待つ」
    async with sem:
        print(f"{name} 開始 {time.strftime('%X')}")
        # await は「本当に待つ」ので、ここで待っている間に他タスクが進む
        await asyncio.sleep(sec)
        print(f"{name} 終了 {time.strftime('%X')}")
        return f"{name} 完了"

async def main():
    print(f"main 開始 {time.strftime('%X')}")

    sem = asyncio.Semaphore(3)  # 同時に3つまで (終わったら次が入る)
    durations = [10, 3, 5, 3, 2, 1, 2, 1]

    # 全タスクを作って一気に走らせる (実行はセマフォが制御)
    # enumerate は (番号, 値) を返す
    tasks = [
        asyncio.create_task(limited_work(sem, f"task-{i+1}", sec))
        for i, sec in enumerate(durations)
    ]

    # ここで全タスクの終了を待つ (結果を受け取る)
    results = await asyncio.gather(*tasks)
    print("結果:", results)

    print(f"main 終了 {time.strftime('%X')}")

if __name__ == "__main__":
    asyncio.run(main())
