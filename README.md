# Python 学習用リポジトリ（土台）

このリポジトリは、Python の個人学習を「散らからず、増えても管理しやすい」形で進めるための土台です。  
各学習テーマは `projects/` 配下に分け、プロジェクト単位で仮想環境を作成します（`.venv` は Git には含めません）。

## 目的

- 学習内容が増えても整理された構成を維持する
- プロジェクト単位で仮想環境（`.venv`）を使えるようにする
- `requirements.txt` ベースで依存管理する
- README だけで運用ルールが分かる状態にする

## ディレクトリ構成

```
.
├── docs/                  # 学習ノート
├── snippets/              # 短いコード片
├── scripts/               # 補助スクリプト
├── projects/
│   └── 00_sandbox/         # 最初のベースプロジェクト
│       ├── README.md
│       ├── requirements.txt
│       ├── src/
│       │   └── main.py
│       └── tests/
│           └── test_smoke.py
└── .gitignore
```

## 仮想環境（venv）

プロジェクトごとに `projects/<project_name>/.venv` を作成します。  
`.venv` は Git 管理しません。

### venv 作成

macOS/Linux:

```
cd projects/00_sandbox
python -m venv .venv
```

Windows PowerShell:

```
cd projects/00_sandbox
python -m venv .venv
```

### activate / deactivate

macOS/Linux:

```
source .venv/bin/activate
deactivate
```

Windows PowerShell:

```
.\.venv\Scripts\Activate.ps1
deactivate
```

### 依存関係インストール

```
pip install -r requirements.txt
```

## 実行方法

```
python src/main.py --name World --count 2
```

## （任意）pytest / ruff

```
pytest
ruff check .
```

## 新しい学習テーマを追加する手順

`projects/01_topic_name` のように追加します。以下をコピペして使えます。

```
# 1) フォルダ作成
mkdir projects/01_topic_name
mkdir projects/01_topic_name/src
mkdir projects/01_topic_name/tests

# 2) README と requirements を作成
# (00_sandbox をベースにしても OK)

# 3) 仮想環境作成（必要なら）
cd projects/01_topic_name
python -m venv .venv

# 4) 依存インストール
pip install -r requirements.txt
```

推奨: `projects/00_sandbox` をコピーして始めると、実行・テストの雛形が揃っていて便利です。
