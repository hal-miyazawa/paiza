# asyncio.Queue を使った「受注 -> 処理」のサンプル。
# 学習ポイント:
# 1) order_receiver が注文をキューに積む
# 2) worker がキューから取り出して処理する
# 3) queue.join() は「put された全件に task_done が対応するまで」待つ
# 補足:
# - create_task(...) は Task を登録するだけで、その場では待たない
# - 実際に待つのは await がある場所（put/get/join/gather など）
# - None はキューのデータとして流す「終了シグナル」(task_done とは別物)
# - put で未完了カウント +1、task_done で -1、join は 0 まで待つ
# - get した件数と task_done の件数がズレると join が解除されない

import asyncio
import time

# 受注は速く、処理は遅くして待ち行列を見える化する
ORDER_INTERVAL_SECONDS = 0.3
WORK_SECONDS = 3.0
WORKER_COUNT = 2


async def order_receiver(order_queue, worker_count):
    customers = ["青山商事", "北川ストア", "中央オフィス", "東和電機", "南野企画"]
    for order_id, customer_name in enumerate(customers, start=1):
        # 受注側は一定間隔で仕事を追加していく（各注文処理の完了は待たない）。
        await asyncio.sleep(ORDER_INTERVAL_SECONDS)
        order = {
            "order_id": order_id,
            "customer_name": customer_name,
            "product": "ノートPC",
            # monotonic は経過時間計測向け。時刻のズレ影響を受けにくい。
            "accepted_at": time.monotonic(),
        }

        # put はコルーチン。maxsize を設定していると満杯時にここで待つ。
        # このサンプルは maxsize=0（上限なし）なので通常はほぼ待たない。
        await order_queue.put(order)
        print(
            f"受注: 注文{order_id} ({customer_name}) {time.strftime('%X')} "
            f"/ キュー滞留: 約{order_queue.qsize()}件"
        )

    # worker ごとに終了シグナル(None)を 1 つずつ送る。
    # これを受けた worker は return して Task 完了になる。
    for _ in range(worker_count):
        await order_queue.put(None)


async def worker(order_queue, worker_name):
    while True:
        # キューが空なら、注文が来るまでここで待機する。
        order = await order_queue.get()
        try:
            if order is None:
                print(f"{worker_name}: 業務終了 {time.strftime('%X')}")
                # return すると「この worker の Task は完了(done)」になる。
                return

            order_id = order["order_id"]
            customer_name = order["customer_name"]
            product = order["product"]
            wait_seconds = time.monotonic() - order["accepted_at"]
            print(
                f"{worker_name}: 処理開始 注文{order_id} ({customer_name}/{product}) {time.strftime('%X')} "
                f"/ 受付から {wait_seconds:.1f} 秒待ち"
            )

            await asyncio.sleep(WORK_SECONDS)
            print(f"{worker_name}: 処理完了 注文{order_id} ({customer_name}/{product}) {time.strftime('%X')}")
        finally:
            # 例外/return でも必ず呼ぶ。join の待機解除に必要。
            # さっき get() で取り出した1件の処理が終わったと伝える
            order_queue.task_done()


async def main():
    print(
        f"main 開始 {time.strftime('%X')} "
        f"(受注間隔={ORDER_INTERVAL_SECONDS}秒, 処理時間={WORK_SECONDS}秒)"
    )

    # デフォルトは maxsize=0（上限なしキュー）。
    order_queue = asyncio.Queue()

    # create_task は待たずに即返る。2本の worker を「起動予約」するイメージ。
    # 複数 worker を先に起動して、注文待ちにしておく。
    workers = [
        asyncio.create_task(worker(order_queue, "worker-1")),
        asyncio.create_task(worker(order_queue, "worker-2")),
    ]

    # ここでは「注文をすべてキューに積む」ところまで進む。
    await order_receiver(order_queue, WORKER_COUNT)

    #キューは入った時点で未完了カウントを持ってるから0になったら先にすすむ
    # put した注文 + 終了シグナルが、すべて task_done されるまでここで待つ。
    await order_queue.join()

    # 各 worker は None を受け取って return 済み。
    # gather は「全 worker Task 完了」まで待ってから戻る。
    # (return した Task をここで最終的に回収する)
    await asyncio.gather(*workers)

    print(f"main 終了 {time.strftime('%X')}")


if __name__ == "__main__":
    asyncio.run(main())
