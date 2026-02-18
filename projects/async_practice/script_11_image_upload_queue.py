# このスクリプトは「画像アップロード処理キュー」の実務イメージを学ぶサンプルです。
# 学べること:
# 1) Queue でアップロード要求を受け渡す
# 2) Worker が並行で処理する
# 3) 外部スキャンAPIを Semaphore + timeout + retry で守る
# 4) 同期処理(サムネイル生成)を to_thread へ逃がす
# 5) join / gather で「仕事完了」と「Task終了」を分けて待つ

import asyncio
import time

# -------- 設定値 --------
WORKER_COUNT = 3
QUEUE_MAXSIZE = 3
SCAN_CONCURRENCY = 2
SCAN_TIMEOUT_SECONDS = 3.0
MAX_RETRY = 2

INGEST_INTERVAL_SECONDS = 1.0
VALIDATION_SECONDS = 0.6
SCAN_OK_SECONDS = 1.4
SCAN_ERROR_SECONDS = 1.2
SCAN_TIMEOUT_EXTRA_SECONDS = 2.2
RETRY_BACKOFF_SECONDS = 1.0
THUMBNAIL_BLOCKING_SECONDS = 1.3
UPLOAD_SECONDS = 1.5

# 実務イメージの入力データ
# scan_plan:
# - "ok": 正常応答
# - "timeout": タイムアウト
# - "error": 一時エラー
UPLOAD_REQUESTS = [
    {"file_id": "IMG-001", "user": "sato", "size_mb": 4.2, "scan_plan": ["ok"]},
    {"file_id": "IMG-002", "user": "tanaka", "size_mb": 7.8, "scan_plan": ["timeout", "ok"]},
    {"file_id": "IMG-003", "user": "suzuki", "size_mb": 3.1, "scan_plan": ["error", "ok"]},
    {"file_id": "IMG-004", "user": "yamada", "size_mb": 31.0, "scan_plan": ["ok"]},  # バリデーション失敗用
    {"file_id": "IMG-005", "user": "ito", "size_mb": 5.5, "scan_plan": ["ok"]},
]


def log(section, message, blank=False):
    """ターミナル上で見やすいログ形式にそろえる。"""
    if blank:
        print()
    print(f"{time.strftime('%X')} | {section:<9} | {message}")


def blocking_generate_thumbnail(file_id):
    """
    同期処理の例。
    画像ライブラリを使った重い処理を想定して time.sleep で代用。

    注意:
    - これを async 関数の中で直接呼ぶとイベントループが止まる。
    - なので worker では asyncio.to_thread(...) で実行する。
    """
    time.sleep(THUMBNAIL_BLOCKING_SECONDS)
    return f"thumb_{file_id}.jpg"


async def receive_upload_requests(upload_queue, worker_count):
    """
    producer 側: アップロード要求を queue に入れる。

    流れ:
    1) 一定間隔でリクエストを queue に投入
    2) すべて投入後、終了シグナル(None)を worker 数ぶん投入
    """
    for req in UPLOAD_REQUESTS:
        await asyncio.sleep(INGEST_INTERVAL_SECONDS)
        await upload_queue.put(req)
        log(
            "INGEST",
            f"受付 {req['file_id']} user={req['user']} size={req['size_mb']}MB / queue={upload_queue.qsize()}",
        )

    # queue の1要素は1workerしか取れないため、終了シグナルは worker 数ぶん必要。
    for _ in range(worker_count):
        await upload_queue.put(None)

    log("INGEST", "受付終了 (stop signal 投入)", blank=True)


async def validate_request(req):
    """
    事前バリデーション。
    実務では拡張子・サイズ・メタデータ整合性チェックなどを行う。
    """
    await asyncio.sleep(VALIDATION_SECONDS)
    if req["size_mb"] > 25:
        raise ValueError(f"file too large: {req['size_mb']}MB")


async def fake_scan_api(req, attempt):
    """外部スキャンAPIの疑似処理。"""
    plan = req["scan_plan"]
    mode = plan[attempt - 1] if attempt - 1 < len(plan) else plan[-1]

    if mode == "timeout":
        await asyncio.sleep(SCAN_TIMEOUT_SECONDS + SCAN_TIMEOUT_EXTRA_SECONDS)
        return {"safe": True}

    if mode == "error":
        await asyncio.sleep(SCAN_ERROR_SECONDS)
        raise RuntimeError("scan service temporary error")

    await asyncio.sleep(SCAN_OK_SECONDS)
    return {"safe": True}


async def scan_with_retry(req, scan_sem):
    """
    外部API呼び出しの保護層。

    1) Semaphore で同時呼び出し数を制限
    2) wait_for で timeout を付与
    3) timeout / 一時エラーは retry
    """
    for attempt in range(1, MAX_RETRY + 2):
        try:
            async with scan_sem:
                log("SCAN", f"call {req['file_id']} attempt={attempt}")
                return await asyncio.wait_for(
                    fake_scan_api(req, attempt),
                    timeout=SCAN_TIMEOUT_SECONDS,
                )
        except asyncio.TimeoutError:
            log("SCAN", f"timeout {req['file_id']} attempt={attempt}")
        except RuntimeError as exc:
            log("SCAN", f"error {req['file_id']} attempt={attempt} reason={exc}")

        if attempt <= MAX_RETRY:
            log("SCAN", f"retry待機 {req['file_id']} {RETRY_BACKOFF_SECONDS}秒")
            await asyncio.sleep(RETRY_BACKOFF_SECONDS)

    raise RuntimeError(f"scan failed after retries: {req['file_id']}")


async def upload_to_storage(req):
    """ストレージ保存の疑似非同期処理。"""
    await asyncio.sleep(UPLOAD_SECONDS)
    return f"https://cdn.example.local/{req['file_id']}.jpg"


async def worker(name, upload_queue, scan_sem, stats, stats_lock):
    """
    consumer 側: queue から取り出して1件ずつ処理。

    1) get で1件取得 (空なら待機)
    2) None なら終了
    3) validate -> scan(retry) -> thumbnail(to_thread) -> upload
    4) 成功/失敗を stats に反映
    5) finally で task_done を必ず通知
    """
    while True:
        req = await upload_queue.get()
        try:
            if req is None:
                log(name, "stop signal 受信 -> 終了", blank=True)
                return

            log(name, f"開始 {req['file_id']} ({req['user']})", blank=True)

            try:
                # 1) 事前チェック
                await validate_request(req)

                # 2) 外部スキャン
                result = await scan_with_retry(req, scan_sem)
                if not result["safe"]:
                    raise RuntimeError("unsafe file detected")

                # 3) 同期処理をスレッドへ逃がす
                thumb_name = await asyncio.to_thread(blocking_generate_thumbnail, req["file_id"])

                # 4) アップロード保存
                url = await upload_to_storage(req)

                # 共有集計は lock で保護して更新
                async with stats_lock:
                    stats["success"] += 1

                log(name, f"完了 {req['file_id']} -> {thumb_name} -> {url}")

            except ValueError as exc:
                # バリデーション失敗
                async with stats_lock:
                    stats["invalid"] += 1
                log(name, f"入力不正 {req['file_id']} reason={exc}")

            except Exception as exc:
                # API失敗や想定外エラー
                async with stats_lock:
                    stats["failed"] += 1
                log(name, f"失敗 {req['file_id']} reason={exc}")

        finally:
            # get で受け取った1件に対応する完了通知。
            # これが漏れると queue.join() が解除されない。
            upload_queue.task_done()


async def main():
    # ---- 起動フェーズ ----
    log("MAIN", "開始", blank=True)
    log(
        "MAIN",
        (
            f"設定 worker={WORKER_COUNT}, queue_max={QUEUE_MAXSIZE}, "
            f"scan_concurrency={SCAN_CONCURRENCY}, timeout={SCAN_TIMEOUT_SECONDS}s"
        ),
    )

    upload_queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
    scan_sem = asyncio.Semaphore(SCAN_CONCURRENCY)

    # worker 全体で共有する集計
    stats = {"success": 0, "invalid": 0, "failed": 0}
    stats_lock = asyncio.Lock()

    # worker を先に起動して queue 待機させる
    workers = [
        asyncio.create_task(worker(f"worker-{i+1}", upload_queue, scan_sem, stats, stats_lock))
        for i in range(WORKER_COUNT)
    ]

    # ---- 投入フェーズ ----
    await receive_upload_requests(upload_queue, WORKER_COUNT)

    # ---- 完了待ちフェーズ ----
    log("MAIN", "queue.join 待機開始", blank=True)
    # queue.join は「putされた全件に task_done が対応するまで」待つ。
    await upload_queue.join()
    log("MAIN", "queue.join 解除 (全件処理完了)")

    log("MAIN", "gather 待機開始 (worker Task 終了待ち)")
    # gather は worker Task 自体の終了を待つ。
    await asyncio.gather(*workers)

    log("MAIN", f"終了 / stats={stats}", blank=True)


if __name__ == "__main__":
    asyncio.run(main())
