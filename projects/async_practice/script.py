import asyncio
import time

async def function_1(sec):
    print(f"{sec}秒待ちます")
    await asyncio.sleep(sec)
    return f"{sec}秒の待機に成功しました。"


#コルーチン化
async def main():
    print(f"main開始 {time.strftime('%X')}")
    #コルーチンにawaitをつけることでその処理が終わるまで待つようになる
    result_1 = await function_1(5)
    print(result_1)
    result_2 = await function_1(6)
    print(result_2)
    print(f"main終了 {time.strftime('%X')}")

#ここが何をしているかを勉強する
if __name__ == "__main__":
    asyncio.run(main())
