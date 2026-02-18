# このスクリプトは「実務寄りの非同期パイプライン」を学びます。
# 学べること:
# 1) Queue で受注を順番に流す
# 2) Worker が並行処理する
# 3) 外部API呼び出しを Semaphore + timeout + retry で守る
# 4) 同期処理(DB保存想定)を to_thread で逃がす
# 5) join/gather で「仕事完了」と「Task終了」を分けて待つ
#
# 全体の流れ:
# A. main が worker を先に起動 (worker は queue.get() で待機)
# B. ingest_orders が注文を queue に入れる
# C. worker が注文を取り出して API -> 保存 を実行
# D. ingest_orders が最後に None(終了シグナル) を worker 数ぶん入れる
# E. main が queue.join() で「全件 task_done 済み」を待つ
# F. main が gather() で「worker Task 自体の終了」を待つ

import asyncio
import time

# -------- 設定値 --------
# worker 数: 同時に注文処理する担当者数
WORKER_COUNT = 3
# queue 上限: これを超える投入は put 側が待つ
QUEUE_MAXSIZE = 4
# 外部API 同時呼び出し上限 (過負荷防止)
API_CONCURRENCY = 2
# 1回のAPI呼び出しタイムアウト
API_TIMEOUT_SECONDS = 4.0
# リトライ回数 (MAX_RETRY=2 なら最大3回試行)
MAX_RETRY = 2

# 実行の見やすさのため、やや遅めの秒数に設定
INGEST_INTERVAL_SECONDS = 1.2
API_OK_SECONDS = 2.2
API_ERROR_SECONDS = 1.8
API_TIMEOUT_EXTRA_SECONDS = 3.0
RETRY_BACKOFF_SECONDS = 1.0
DB_SAVE_SECONDS = 1.5


# 実務イメージの入力データ。
# plan:
# - "ok": 正常応答
# - "timeout": タイムアウトになる遅延応答
# - "error": 一時エラー
ORDERS = [
    {"id": "ORD-1001", "customer": "青山商事", "amount": 120000, "plan": ["ok"]},
    {"id": "ORD-1002", "customer": "北川ストア", "amount": 54000, "plan": ["timeout", "ok"]},
    {"id": "ORD-1003", "customer": "中央オフィス", "amount": 330000, "plan": ["error", "ok"]},
    {"id": "ORD-1004", "customer": "東和電機", "amount": 90000, "plan": ["ok"]},
    {"id": "ORD-1005", "customer": "南野企画", "amount": 75000, "plan": ["timeout", "timeout", "ok"]},
    {"id": "ORD-1006", "customer": "西原物流", "amount": 41000, "plan": ["ok"]},
]


def log(section, message, blank=False):
    """見やすいログ形式で表示する。"""
    if blank:
        print()
    print(f"{time.strftime('%X')} | {section:<7} | {message}")


def blocking_save(order_id, score):
    """
    同期処理の例: DB保存/ファイル書き込みを想定。

    ここはブロッキング処理なので、worker から直接呼ぶとイベントループを止める。
    そのため worker 側では asyncio.to_thread(...) 経由で実行する。
    """
    time.sleep(DB_SAVE_SECONDS)
    log("DB", f"保存完了 {order_id} score={score}")


async def ingest_orders(order_queue, worker_count):
    """
    受注を queue に投入する producer 側。

    ポイント:
    - await order_queue.put(...) は queue が満杯なら待機する
    - 最後に None を worker 数ぶん投入し、worker に終了を伝える
    """
    for order in ORDERS:
        await asyncio.sleep(INGEST_INTERVAL_SECONDS)
        await order_queue.put(order)
        log(
            "INGEST",
            f"受付 {order['id']} ({order['customer']}) / queue={order_queue.qsize()}",
        )

    for _ in range(worker_count):
        await order_queue.put(None)

    log("INGEST", "受付終了 (stop signal 投入)", blank=True)


async def fake_external_api(order, attempt):
    """
    外部APIの疑似処理。
    order["plan"] に応じて timeout/error/ok を返す。
    """
    plan = order["plan"]
    mode = plan[attempt - 1] if attempt - 1 < len(plan) else plan[-1]

    if mode == "timeout":
        # timeout を発生させるため、制限時間より長く待つ。
        await asyncio.sleep(API_TIMEOUT_SECONDS + API_TIMEOUT_EXTRA_SECONDS)
        return {"score": 0}

    if mode == "error":
        await asyncio.sleep(API_ERROR_SECONDS)
        raise RuntimeError("temporary upstream error")

    await asyncio.sleep(API_OK_SECONDS)
    score = 95 if order["amount"] >= 100000 else 80
    return {"score": score}


async def call_api_with_retry(order, api_sem):
    """
    API呼び出しの保護層。

    1) Semaphore で同時呼び出し数を制限
    2) wait_for で1回のタイムアウトを制御
    3) timeout / 一時エラー時はリトライ
    """
    for attempt in range(1, MAX_RETRY + 2):
        try:
            # ここを通るのは同時に API_CONCURRENCY 件まで
            async with api_sem:
                log("API", f"call {order['id']} attempt={attempt}")
                return await asyncio.wait_for(
                    fake_external_api(order, attempt),
                    timeout=API_TIMEOUT_SECONDS,
                )
        except asyncio.TimeoutError:
            log("API", f"timeout {order['id']} attempt={attempt}")
        except RuntimeError as exc:
            log("API", f"error {order['id']} attempt={attempt} reason={exc}")

        if attempt <= MAX_RETRY:
            log("API", f"retry待機 {order['id']} {RETRY_BACKOFF_SECONDS}秒")
            await asyncio.sleep(RETRY_BACKOFF_SECONDS)

    raise RuntimeError(f"API failed after retries: {order['id']}")


async def worker(name, order_queue, api_sem, stats, stats_lock):
    """
    queue を読み続ける consumer 側。

    1件ごとの処理:
    - queue.get() で取得 (空なら待つ)
    - None なら終了
    - API呼び出し + DB保存
    - 成功/失敗を stats に反映
    - finally で task_done() を必ず呼ぶ
    """
    while True:
        order = await order_queue.get()
        try:
            if order is None:
                log(name, "stop signal 受信 -> 終了", blank=True)
                return

            log(name, f"開始 {order['id']} ({order['customer']})", blank=True)

            try:
                result = await call_api_with_retry(order, api_sem)

                # 同期保存処理をスレッドへ逃がす（イベントループを止めない）
                await asyncio.to_thread(blocking_save, order["id"], result["score"])

                # stats は共有データなので lock で保護して更新
                async with stats_lock:
                    stats["success"] += 1

                log(name, f"完了 {order['id']}")
            except Exception as exc:
                # 注文単位の失敗として記録し、worker 全体は継続する
                async with stats_lock:
                    stats["failed"] += 1
                log(name, f"失敗 {order['id']} reason={exc}")
        finally:
            # get で受け取った1件に対する完了通知。
            # これが不足すると queue.join() が解除されない。
            order_queue.task_done()


async def main():
    # -------- 起動フェーズ --------
    log("MAIN", "開始", blank=True)
    log(
        "MAIN",
        (
            f"設定 worker={WORKER_COUNT}, queue_max={QUEUE_MAXSIZE}, "
            f"api_concurrency={API_CONCURRENCY}, timeout={API_TIMEOUT_SECONDS}s"
        ),
    )

    order_queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
    api_sem = asyncio.Semaphore(API_CONCURRENCY)

    # 全workerで共有する集計オブジェクト
    stats = {"success": 0, "failed": 0}
    stats_lock = asyncio.Lock()

    # worker を先に起動して、queue.get() 待機状態にしておく
    workers = [
        asyncio.create_task(worker(f"worker-{i+1}", order_queue, api_sem, stats, stats_lock))
        for i in range(WORKER_COUNT)
    ]

    # -------- 投入フェーズ --------
    await ingest_orders(order_queue, WORKER_COUNT)

    # -------- 完了待ちフェーズ --------
    log("MAIN", "queue.join 待機開始", blank=True)
    # queue.join は「put された全件に task_done が対応するまで」待つ。
    await order_queue.join()
    log("MAIN", "queue.join 解除 (全件 task_done 済み)")

    log("MAIN", "gather 待機開始 (worker Task 終了待ち)")
    # gather は worker Task 自体の終了を待つ。
    # (None を受けて return した Task をここで回収)
    await asyncio.gather(*workers)

    log("MAIN", f"終了 / stats={stats}", blank=True)


if __name__ == "__main__":
    asyncio.run(main())
