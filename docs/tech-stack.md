# 技術スタック / Tech Stack

## バックエンド (Backend)

| 技術 | バージョン | 用途 |
|---|---|---|
| Python | 3.11+ | メイン言語 |
| FastAPI | latest | REST API サーバー |
| Uvicorn | latest | ASGI サーバー |
| SQLAlchemy | 2.x | ORM |
| Alembic | latest | DB マイグレーション |
| APScheduler | latest | 定期実行スケジューラ |
| hyperliquid-python-sdk | latest | Hyperliquid API クライアント |
| pandas | latest | データ処理・指標計算 |
| ta-lib / pandas-ta | latest | テクニカル指標ライブラリ |
| LangChain | latest | AI エージェントフレームワーク |
| LangGraph | latest | エージェント間のグラフ制御 |
| httpx | latest | 非同期 HTTP クライアント |
| pydantic | v2 | データバリデーション |

## フロントエンド (Frontend)

| 技術 | バージョン | 用途 |
|---|---|---|
| Next.js | 14+ (App Router) | React フレームワーク |
| TypeScript | 5+ | 型安全な JS |
| Tailwind CSS | 3+ | ユーティリティファースト CSS |
| SWR / TanStack Query | latest | データフェッチ・キャッシュ |
| recharts / Chart.js | latest | チャート描画 |
| shadcn/ui | latest | UI コンポーネント |

## データベース (Database)

| 技術 | バージョン | 用途 |
|---|---|---|
| MySQL | 8.x | メインデータベース |

## インフラ (Infrastructure)

| 技術 | 用途 |
|---|---|
| Docker | コンテナ化 |
| Docker Compose | マルチコンテナ管理 |

## AI / LLM

| 技術 | 用途 |
|---|---|
| Anthropic Claude API | 主要 LLM（推奨） |
| OpenAI API | 代替 LLM |
| LangChain | LLM 連携・プロンプト管理 |
| LangGraph | エージェントグラフ・状態管理 |

## 開発ツール

| ツール | 用途 |
|---|---|
| uv | Python パッケージ管理 |
| Ruff | Linter / Formatter |
| pytest | テストフレームワーク |
| pre-commit | コミット前フック |

## ディレクトリ構成（想定）

```
magi-trade/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI エントリーポイント
│   │   ├── api/                 # APIルーター
│   │   │   ├── position.py
│   │   │   ├── logs.py
│   │   │   ├── history.py
│   │   │   └── settings.py
│   │   ├── core/
│   │   │   ├── config.py        # 設定・環境変数
│   │   │   └── database.py      # DB 接続
│   │   ├── models/              # SQLAlchemy モデル
│   │   ├── schemas/             # Pydantic スキーマ
│   │   ├── services/
│   │   │   ├── data_collector.py   # データ取得
│   │   │   ├── indicators.py       # 指標計算
│   │   │   ├── agents/             # AI エージェント
│   │   │   │   ├── trend_agent.py
│   │   │   │   ├── contrarian_agent.py
│   │   │   │   ├── risk_agent.py
│   │   │   │   └── master_agent.py
│   │   │   ├── executor.py         # 注文実行
│   │   │   └── trailing_stop.py    # トレーリングストップ
│   │   └── scheduler.py         # 定期実行ループ
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   ├── components/
│   │   └── lib/
│   ├── Dockerfile
│   └── package.json
├── docs/                        # このフォルダ
├── docker-compose.yml
├── .env.example
└── TASKS.md
```

## 環境変数一覧（`.env.example`）

```env
# Hyperliquid
HL_WALLET_ADDRESS=
HL_PRIVATE_KEY=

# LLM API
ANTHROPIC_API_KEY=
# OPENAI_API_KEY=

# MySQL
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=magi
MYSQL_PASSWORD=
MYSQL_DATABASE=magi_trade

# App
RISK_PERCENT=1.0
DEFAULT_LEVERAGE=5
MAX_HOLD_HOURS=24
```
