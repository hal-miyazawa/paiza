# -*- coding: utf-8 -*-
# このスクリプトは、ユーザーの日本語入力から「タイトル」と「メモ」を提案する
# TODO作成アシスタントの最小CLI版です。
# タスク管理アプリの入力フォーム自動生成（タイトル/メモのたたき台）に活かせます。

import json
import os
from openai import OpenAI
from pydantic import BaseModel

# 返してほしい構造を定義します（Structured Outputs の schema になります）
class TodoProposal(BaseModel):
    title: str
    memo: str


def main():
    # APIキーは環境変数 OPENAI_API_KEY から読み込みます
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY が未設定です。PowerShell で setx OPENAI_API_KEY \"...\" を実行してください。")

    user_text = input("相談内容> ").strip()
    if not user_text:
        raise SystemExit("入力が空です。日本語でやりたいことを入力してください。")

    client = OpenAI()

    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {
                "role": "system",
                "content": (
                    "あなたはTODO作成アシスタントです。\n"
                    "ユーザーの日本語入力から、短いタイトルと補足メモを作ってください。\n"
                    "タイトルは短く、メモは具体的に書きます。\n"
                ),
            },
            {"role": "user", "content": user_text},
        ],
        text_format=TodoProposal,
    )

    proposal = response.output_parsed
    print(json.dumps(proposal.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
