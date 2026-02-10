import asyncio
import time

# 複数タスクを同時進行させる基本例
#コルーチン化
async def main():
    print(f"main開始 {time.strftime('%X')}")
    # create_task でコルーチンを「タスク化」すると並行に動き始める
    task1 = asyncio.create_task(asyncio.sleep(5))
    task2 = asyncio.create_task(asyncio.sleep(10))
    # await で完了を待つ (この時点では両方とも同時に進行中)
    await task1
    await task2
    # 「戻ったと同時に値を受け取る」 → result = await task
    # 「あとから結果を確認する」 → task.result()
    # asyncio.sleep の戻り値は None。task.result() で確認できる
    print(f"{task1.result()}")
    print(f"{task2.result()}")
    print(f"main終了 {time.strftime('%X')}")



if __name__ == "__main__":
    asyncio.run(main())
