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

## 9. よくあるトラブル

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
