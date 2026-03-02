# タスク管理 / Task Board

Hyperliquid AI-Driven Multi-Agent Trading System の開発タスク一覧。

## ステータス凡例

| 記号 | 意味 |
|---|---|
| `[ ]` | 未着手 |
| `[~]` | 進行中 |
| `[x]` | 完了 |

---

## Step 1: 基礎インフラとデータ取得ロジックの実装

### インフラ構築

- [x] `docker-compose.yml` の作成（MySQL / FastAPI / Next.js）
- [x] MySQL コンテナの設定（ボリューム・初期化スクリプト）
- [x] FastAPI コンテナの設定（Dockerfile）
- [x] `.env.example` の作成
- [x] Alembic によるマイグレーション環境の構築

### データベース設計・実装

- [x] `market_data` テーブルの作成（OHLCV）
- [x] `funding_rates` テーブルの作成
- [x] `hlp_data` テーブルの作成
- [x] `agent_sessions` テーブルの作成
- [x] `agent_opinions` テーブルの作成
- [x] `final_decisions` テーブルの作成
- [x] `trades` テーブルの作成
- [x] `trade_settings` テーブルの作成

### データ取得モジュール

- [x] `hyperliquid-python-sdk` の導入・接続確認
- [x] OHLCV データ取得モジュールの実装（1m / 15m / 30m / 1h）
- [x] Funding Rate 取得モジュールの実装
- [x] HLP データ取得モジュールの実装
- [x] 取得データの MySQL 保存ロジックの実装
- [x] 重複保存防止（UPSERT 等）の実装

### データ整形・変換

- [x] テクニカル指標計算モジュールの実装（RSI / EMA / ATR / MACD / BB）
- [x] AI へ渡す JSON フォーマット生成ロジックの実装

---

## Step 2: AI Multi-Agent 合議システムの構築

### LLM 連携

- [x] LLM クライアント抽象基底クラス `LLMClient` の実装（CLI / API 共通インターフェース）
- [x] CLI バックエンドの実装
  - [x] GitHub Copilot CLI クライアント（新スタンドアロン `copilot` コマンド対応）
  - [x] Claude Code CLI クライアント（`claude -p`）
  - [x] Codex CLI クライアント（`codex --quiet`）
  - [x] Gemini CLI クライアント（`gemini --prompt`）
- [x] モック LLM クライアント（テスト・ドライラン用）
- [x] LLM バックエンドファクトリ（`create_llm_client()`）
- [x] プロンプトテンプレート管理モジュールの作成

### エージェント実装

- [x] `TradingState` / `AgentOpinionData` / `MasterDecisionData` の型定義
- [x] Trend Agent のプロンプト設計・実装
- [x] Contrarian Agent のプロンプト設計・実装
- [x] Risk Agent のプロンプト設計・実装
- [x] Master Agent の集約ロジック・プロンプト設計・実装

### LangGraph 統合

- [x] LangGraph グラフの構築（sub_agents → master → save の逐次 + 内部 asyncio.gather で並列）
- [x] エージェントの並列実行（asyncio.gather）

### 保存・ログ

- [x] 各エージェントの意見を DB に保存する実装
- [x] マスターエージェントの最終判断を DB に保存する実装
- [x] 議論ログの取得 API エンドポイントの実装（`GET /api/logs`）
- [x] スケジューラへのエージェントサイクル統合（15分ごと自動実行）

---

## Step 3: 取引実行エンジンとリスク管理の実装

### 注文実行

- [ ] Hyperliquid API による成行注文の実装
- [ ] Hyperliquid API による指値注文の実装
- [ ] 注文結果の DB 保存の実装

### リスク管理

- [ ] 固定パーセントモデルによる投入額計算の実装
- [ ] ATR ベースの初期 SL 自動計算の実装
- [ ] リスクリワード比ベースの初期 TP 自動計算の実装
- [ ] AI 判断に基づく TP 更新ロジックの実装

### トレーリングストップ

- [ ] トレーリングストップ常駐プロセスの実装
- [ ] ATR ベースのトレーリング幅計算の実装
- [ ] SL 更新（有利方向への移動）ロジックの実装
- [ ] トレーリングストップ発動時の決済処理の実装

### メインループ

- [ ] 15分足ごとのメインループ処理の実装（APScheduler）
- [ ] 最大ホールド期間チェックロジックの実装
- [ ] Funding Rate コスト監視の実装

---

## Step 4: WebUI（Next.js）ダッシュボード開発

### プロジェクト基盤

- [ ] Next.js プロジェクトの初期化（App Router / TypeScript / Tailwind）
- [ ] FastAPI との API 連携設定（fetch / SWR）
- [ ] 認証・アクセス制限の実装（オプション）

### ダッシュボード画面

- [ ] 現在のポジション表示コンポーネント
- [ ] 有効証拠金・未実現損益の表示
- [ ] リアルタイム更新（ポーリング or WebSocket）

### 議論ログビューア

- [ ] AI 議論ログ一覧の取得・表示
- [ ] チャット風 UI の実装（エージェント別色分け）
- [ ] マスターエージェントの最終判断の強調表示

### 取引履歴

- [ ] 取引履歴一覧のテーブル表示
- [ ] 各取引の詳細（判断根拠・議論ログ）へのリンク

### 設定画面

- [ ] リスク率・レバレッジ等の設定表示
- [ ] 設定変更フォームと API 連携

### FastAPI エンドポイント（フロント向け）

- [ ] `GET /api/position` — 現在のポジション
- [ ] `GET /api/logs` — 議論ログ一覧
- [ ] `GET /api/history` — 取引履歴
- [ ] `GET /api/settings` — 設定取得
- [ ] `PUT /api/settings` — 設定更新

---

## Step 5: 統合テストと自動運用の最適化

### テスト

- [ ] データ取得モジュールの単体テスト
- [ ] 指標計算モジュールの単体テスト
- [ ] AI エージェントの統合テスト（モック LLM 使用）
- [ ] 注文実行エンジンのテスト（Testnet 使用）
- [ ] フルシーケンスの E2E テスト

### エラーハンドリング強化

- [ ] Hyperliquid API エラー時のリトライロジック
- [ ] LLM API エラー時のフォールバック（多数決へ切り替え等）
- [ ] タイムアウト処理の実装
- [ ] エラー通知の実装（ログ / Slack 等）

### デプロイメント検証

- [ ] 自宅サーバーへの Docker Compose デプロイ検証
- [ ] 環境変数・シークレット管理の確認
- [ ] ログローテーションの設定
- [ ] モニタリング（Uptime / メモリ / CPU）の設定

---

## バックログ / 将来対応

- [ ] マルチシンボル対応（BTC 以外のペアへの拡張）
- [ ] バックテスト機能の実装
- [ ] Slack / LINE 通知連携
- [ ] AI モデルのパフォーマンス評価・自動チューニング
- [ ] ペーパートレードモードの実装

---

## メモ / 注意事項

- API Key・Secret は `.env` で管理し、**絶対に DB や Git に含めない**
- Hyperliquid Testnet で十分テストしてから本番に移行する
- LLM API のコストを監視し、不要なリクエストを最小化する
- ポジションサイズは必ず固定パーセントモデルで計算し、過大投入を防ぐ
