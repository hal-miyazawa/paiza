# -*- coding: utf-8 -*-
# このサーバは、簡素なフロント（フォーム + AI相談モーダル）を配信し、
# AIに相談文を送ると「タイトル」と「メモ」を返して画面に反映する最小デモです。
# 目的：Reactでの画面反映フローと、OpenAI APIの連携を理解すること。
# DBは使わず、保存は行いません（フォーム反映まで）。

from __future__ import annotations

import os
from flask import Flask, jsonify, render_template, request
from openai import OpenAI
from pydantic import BaseModel

app = Flask(__name__)


# 返してほしい構造を定義（Structured Outputs）
class TodoProposal(BaseModel):
    title: str
    memo: str

#ブラウザで http://127.0.0.1:8000/ を開いた時に、index.html を返す
@app.get("/")
def index():
    # 最小の画面を返す
    return render_template("index.html")


@app.post("/api/propose")
def propose():
    # 入力取得
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "相談内容が空です"}), 400

    # APIキーは環境変数から取得
    if not os.environ.get("OPENAI_API_KEY"):
        return jsonify({"error": "OPENAI_API_KEY が未設定です"}), 500


    # OpenAI APIを使うためのクライアント（接続口）
    client = OpenAI()

    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            # システム側の設定
            {
                "role": "system",
                "content": (
                    "あなたはTODO作成アシスタントです。\n"
                    "ユーザーの日本語入力から、短いタイトルと補足メモを作ってください。\n"
                    "タイトルは短く、メモは具体的に書きます。"
                ),
            },
            #ユーザー側で入力したのを送るほう
            {"role": "user", "content": text},
        ],
        text_format=TodoProposal,
    )

    # AIの返答は TodoProposal型（title/memo）
    proposal = response.output_parsed
    # ythonオブジェクト → 辞書（dict） に変換して返す
    return jsonify(proposal.model_dump())


if __name__ == "__main__":
    # ローカル起動用
    app.run(host="127.0.0.1", port=8000, debug=True)
