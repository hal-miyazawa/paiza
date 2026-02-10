import asyncio
import time

# 最小の非同期例: await で「終わるまで待つ」動きを確認する
async def function_1(sec):
    # async def はコルーチン関数。呼び出すと「実行待ち」のコルーチンになる
    print(f"{sec}秒待ちます")
    # await するとイベントループに制御を戻し、他の処理が動ける
    await asyncio.sleep(sec)
    return f"{sec}秒の待機に成功しました。"


#コルーチン化
async def main():
    print(f"main開始 {time.strftime('%X')}")
    # コルーチンに await を付けると、その処理が終わるまで次へ進まない
    # (ここでは順番に待つため、合計で 5 秒 + 6 秒 かかる)
    result_1 = await function_1(5)
    print(result_1)
    result_2 = await function_1(6)
    print(result_2)
    print(f"main終了 {time.strftime('%X')}")

#ここが何をしているかを勉強する
if __name__ == "__main__":
    # asyncio.run がイベントループを作り、main() を最後まで動かす
    asyncio.run(main())
