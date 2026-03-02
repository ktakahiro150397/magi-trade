# セットアップガイド

ローカル環境での開発用セットアップ手順です。Docker Compose を使って MySQL / FastAPI / Next.js の3コンテナを起動します。

---

## 前提条件

| ツール | バージョン | 確認コマンド |
|---|---|---|
| Docker | 24.x 以上 | `docker --version` |
| Docker Compose | 2.x 以上 | `docker compose version` |
| Git | 任意 | `git --version` |

---

## 1. リポジトリのクローン

```bash
git clone https://github.com/ktakahiro150397/magi-trade.git
cd magi-trade
```

---

## 2. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、各値を入力します。

```bash
cp .env.example .env
```

### `.env` 設定項目

```env
# ---- Hyperliquid ----
# Hyperliquid ウォレットアドレス（0x から始まる）
HL_WALLET_ADDRESS=0xYourWalletAddress

# Hyperliquid 秘密鍵（0x から始まる 64 文字の hex）
# ⚠️ 絶対に Git にコミットしないこと
HL_PRIVATE_KEY=0xYourPrivateKey

# ---- LLM API ----
# Anthropic API キー（主要 LLM）
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI API キー（代替 LLM、使用しない場合は空欄でも可）
# OPENAI_API_KEY=sk-...

# ---- MySQL ----
MYSQL_HOST=db               # Docker Compose 内ではサービス名 "db" を使用
MYSQL_PORT=3306
MYSQL_USER=magi
MYSQL_PASSWORD=任意のパスワード
MYSQL_ROOT_PASSWORD=任意のrootパスワード
MYSQL_DATABASE=magi_trade

# ---- トレード設定 ----
RISK_PERCENT=1.0            # 口座残高に対するリスク率 (%)
DEFAULT_LEVERAGE=5          # デフォルトレバレッジ
MAX_HOLD_HOURS=24           # 最大ホールド時間
```

> **注意**: `.env` ファイルは `.gitignore` に含めてください。秘密鍵・API キーは絶対にリポジトリにコミットしないでください。

---

## 3. コンテナのビルドと起動

### 初回起動

```bash
docker compose up --build
```

イメージのビルドと全コンテナの起動が行われます。初回は数分かかります。

### バックグラウンド起動（2回目以降）

```bash
docker compose up -d
```

### サービスごとの起動

```bash
# バックエンドのみ（DB も一緒に起動）
docker compose up -d db backend

# フロントエンドのみ
docker compose up -d frontend
```

---

## 4. DB マイグレーションの実行

コンテナ起動後、Alembic で DB スキーマを作成します。

```bash
docker compose exec backend alembic upgrade head
```

マイグレーション後、MySQL に全テーブルが作成されます。

### マイグレーション状態の確認

```bash
docker compose exec backend alembic current
```

### マイグレーション履歴の確認

```bash
docker compose exec backend alembic history
```

---

## 5. 動作確認

### バックエンド（FastAPI）

```bash
# ヘルスチェック
curl http://localhost:8000/health
# => {"status":"ok"}

# API ドキュメント（Swagger UI）
open http://localhost:8000/docs

# 設定取得
curl http://localhost:8000/api/settings
```

### フロントエンド（Next.js）

```
open http://localhost:3000
```

### DB への接続確認

```bash
docker compose exec db mysql -u magi -p magi_trade
# パスワードを入力後
mysql> SHOW TABLES;
```

---

## 6. スケジューラーの起動

15分ごとのデータ収集ループを起動します（バックエンドコンテナ内で実行）。

```bash
docker compose exec backend python -m app.scheduler
```

> 本番運用では `docker-compose.yml` の `backend` コマンドをスケジューラーに切り替えるか、別サービスとして定義することを推奨します。

---

## 7. コンテナの停止

```bash
# コンテナのみ停止（データは保持）
docker compose stop

# コンテナの削除（データは保持）
docker compose down

# コンテナ + ボリューム（DB データ）の完全削除
docker compose down -v
```

---

## 8. ローカル開発（Docker なし）

Docker を使わずにバックエンドをローカルで動かす場合の手順です。

### Python 環境のセットアップ

```bash
cd backend

# uv のインストール（未インストールの場合）
pip install uv

# 依存パッケージのインストール
uv pip install -e ".[dev]"
```

### FastAPI の起動

```bash
# バックエンドディレクトリで実行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### テストの実行

```bash
cd backend
pytest -v
```

---

## 9. AI エージェントのテスト動作確認

### 9-1. LLM バックエンドの設定

`.env` で使用するバックエンドを選択します。

```env
# ---- LLM バックエンド ----
# まずはモックで動作確認する（実際の CLI は不要）
LLM_BACKEND=mock

# GitHub Copilot CLI を使う場合
# LLM_BACKEND=copilot_cli
# GH_TOKEN=ghp_...   # fine-grained PAT（"Copilot Requests" 権限が必要）

# Claude Code CLI を使う場合
# LLM_BACKEND=claude_code_cli

# Codex CLI を使う場合
# LLM_BACKEND=codex_cli
# OPENAI_API_KEY=sk-...

# Gemini CLI を使う場合
# LLM_BACKEND=gemini_cli
# GOOGLE_API_KEY=...
```

### 9-2. モック応答でエージェントサイクルを1回手動実行

`LLM_BACKEND=mock` の状態で Docker コンテナを起動し、エージェントサイクルを
手動で呼び出します。

```bash
# コンテナを起動（DB + バックエンド）
docker compose up -d db backend

# マイグレーション（初回のみ）
docker compose exec backend alembic upgrade head

# Python コンソールでエージェントサイクルを1回実行
docker compose exec backend python - <<'EOF'
import asyncio
from app.core.database import AsyncSessionLocal
from app.services.agents import run_agent_session
from app.services.indicators import generate_ai_payload
from app.services.llm import create_llm_client

async def main():
    async with AsyncSessionLocal() as db:
        # 市場データペイロード生成（DBにデータがない場合は空になる）
        payload = await generate_ai_payload(db, symbol="BTC")

        # 市場データが空の場合はダミーデータを使用
        if not payload.get("current_price"):
            payload = {
                "symbol": "BTC",
                "generated_at": "2024-01-01T00:00:00",
                "current_price": 50000.0,
                "primary_timeframe": "15m",
                "ohlcv": [],
                "indicators": {},
                "funding_rate": None,
            }

        client = create_llm_client()   # LLM_BACKEND=mock を使用
        print(f"LLM backend: {client.name}")

        state = await run_agent_session(market_data=payload, client=client, db=db)
        decision = state.get("final_decision")
        print(f"Final decision: action={decision.action} confidence={decision.confidence:.2f}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Session ID: {state.get('session_id')}")

asyncio.run(main())
EOF
```

### 9-3. DB 内容の確認

エージェントサイクル実行後、MySQL に結果が保存されていることを確認します。

```bash
docker compose exec db mysql -u magi -p magi_trade
```

MySQL プロンプトで以下を実行します。

```sql
-- エージェントセッション一覧
SELECT id, created_at FROM agent_sessions ORDER BY id DESC LIMIT 5;

-- 各エージェントの意見
SELECT s.id AS session_id, o.agent_name, o.action, o.confidence, LEFT(o.reasoning, 60) AS reasoning
FROM agent_sessions s
JOIN agent_opinions o ON o.session_id = s.id
ORDER BY s.id DESC, o.agent_name;

-- マスターエージェントの最終判断
SELECT s.id AS session_id, d.action, d.confidence, LEFT(d.reasoning, 80) AS reasoning
FROM agent_sessions s
JOIN final_decisions d ON d.session_id = s.id
ORDER BY s.id DESC
LIMIT 5;
```

### 9-4. API エンドポイントで議論ログを取得

```bash
# 最新 20 件のエージェントセッション（意見 + 最終判断）を取得
curl -s http://localhost:8000/api/logs | python3 -m json.tool | head -60
```

### 9-5. ユニットテストの実行（Docker なし・モック使用）

DB や LLM CLI なしでテスト全件を実行できます。

```bash
cd backend
pytest tests/test_llm_client.py tests/test_agents.py tests/test_data_collector.py -v
```

出力例:
```
tests/test_llm_client.py::TestExtractJson::test_plain_json PASSED
tests/test_agents.py::TestRunAgentSession::test_full_workflow_with_mock_db PASSED
...
35 passed in 1.34s
```

---

## 10. GitHub Copilot CLI のセットアップ

GitHub Copilot CLI（新しいスタンドアロン版 `copilot` コマンド）を使う手順です。

> **参考:** [GitHub Copilot CLI 公式ドキュメント](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli)

### 認証トークンの取得

1. GitHub の Settings → Developer settings → Personal access tokens → Fine-grained tokens へ移動
2. 新規トークンを生成し、**Copilot Requests** 権限を付与
3. 生成したトークンを `.env` の `GH_TOKEN` に設定

```env
LLM_BACKEND=copilot_cli
GH_TOKEN=ghp_your_token_here
```

### 動作確認

```bash
# コンテナ内で copilot CLI が使えるか確認
docker compose exec backend copilot --version

# エージェントサイクルをモックから Copilot CLI に切り替えて実行
# （.env の LLM_BACKEND=copilot_cli にした後、コンテナを再起動）
docker compose restart backend
```

---

## 11. よくあるトラブル

### MySQL コンテナが起動しない

- `MYSQL_ROOT_PASSWORD` が未設定の場合に起動に失敗します。`.env` で設定してください。
- ポート 3306 が別プロセスで使用中の場合は `docker-compose.yml` のホストポートを変更してください（例: `"3307:3306"`）。

### `alembic upgrade head` が失敗する

- MySQL コンテナが完全に起動する前に実行すると失敗することがあります。数秒待ってから再実行してください。

```bash
docker compose up -d db
# MySQL が起動するまで待機
sleep 10
docker compose exec backend alembic upgrade head
```

### `hyperliquid-python-sdk` の接続エラー

- Hyperliquid API はメインネット／テストネットの両方に接続できます。
- テスト時は `data_collector.py` 内の `constants.MAINNET_API_URL` を `constants.TESTNET_API_URL` に変更してください。

### `copilot` コマンドが見つからない

- Docker イメージに `copilot` CLI が含まれていることを確認してください。
- または `Dockerfile` に以下を追加します：

```dockerfile
# GitHub Copilot CLI のインストール
RUN curl -fsSL https://github.com/github/copilot-cli/releases/latest/download/copilot-linux-amd64 \
    -o /usr/local/bin/copilot && chmod +x /usr/local/bin/copilot
```

### LLM バックエンドのタイムアウト

- デフォルトのタイムアウトは 120 秒です。`.env` の `LLM_TIMEOUT` で変更可能です。
- CLI ツールのレスポンスが遅い場合は `LLM_TIMEOUT=180` のように延長してください。
