# Magi Trade

Hyperliquid 向け AI マルチエージェント自動売買システム。

Trend / Contrarian / Risk の3エージェントが合議し、Master エージェントが最終判断を下すアーキテクチャです。

---

## ドキュメント

| ドキュメント | 内容 |
|---|---|
| [docs/setup.md](docs/setup.md) | **セットアップ手順**（環境変数・ビルド・起動） |
| [docs/overview.md](docs/overview.md) | プロジェクト概要・要件定義 |
| [docs/architecture.md](docs/architecture.md) | システムアーキテクチャ設計 |
| [docs/tech-stack.md](docs/tech-stack.md) | 技術スタック詳細・ディレクトリ構成 |
| [docs/ai-agent-design.md](docs/ai-agent-design.md) | AI エージェント設計 |
| [docs/risk-management.md](docs/risk-management.md) | リスク管理ロジック |
| [TASKS.md](TASKS.md) | 開発タスク管理 |

---

## クイックスタート

```bash
# 1. リポジトリのクローン
git clone https://github.com/ktakahiro150397/magi-trade.git
cd magi-trade

# 2. 環境変数の設定
cp .env.example .env
# .env を編集して API キー等を入力

# 3. ビルド & 起動
docker compose up --build -d

# 4. DB マイグレーション
docker compose exec backend alembic upgrade head
```

詳細は [docs/setup.md](docs/setup.md) を参照してください。

---

## システム構成

```
magi-trade/
├── backend/                   # FastAPI バックエンド (Python 3.11)
│   ├── app/
│   │   ├── main.py            # FastAPI エントリーポイント
│   │   ├── api/               # REST API エンドポイント
│   │   ├── core/              # 設定・DB 接続
│   │   ├── models/            # SQLAlchemy モデル
│   │   ├── services/
│   │   │   ├── data_collector.py  # Hyperliquid データ取得
│   │   │   ├── indicators.py      # テクニカル指標計算
│   │   │   └── agents/            # AI エージェント（Step 2）
│   │   └── scheduler.py       # 15分足ループ（APScheduler）
│   ├── alembic/               # DB マイグレーション
│   └── tests/                 # 単体テスト
├── frontend/                  # Next.js フロントエンド（Step 4）
├── docs/                      # ドキュメント
├── docker-compose.yml
└── .env.example
```

---

## 開発ステップ

| ステップ | 内容 | 状態 |
|---|---|---|
| Step 1 | 基礎インフラ・データ取得ロジック | ✅ 完了 |
| Step 2 | AI マルチエージェント合議システム | 未着手 |
| Step 3 | 取引実行エンジン・リスク管理 | 未着手 |
| Step 4 | Next.js ダッシュボード | 未着手 |
| Step 5 | 統合テスト・自動運用最適化 | 未着手 |
