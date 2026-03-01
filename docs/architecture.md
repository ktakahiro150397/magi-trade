# システムアーキテクチャ設計

## 全体構成図

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐   ┌───────────────┐  │
│  │   Next.js    │    │   FastAPI    │   │     MySQL     │  │
│  │  (Frontend)  │◄──►│  (Backend)   │◄──►│  (Database)   │  │
│  │  Port: 3000  │    │  Port: 8000  │   │  Port: 3306   │  │
│  └──────────────┘    └──────┬───────┘   └───────────────┘  │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │  AI Agent Core  │                      │
│                    │  (LangGraph)    │                      │
│                    └────────┬────────┘                      │
│                             │                               │
└─────────────────────────────┼───────────────────────────────┘
                              │ HTTP / WebSocket
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
   │ Hyperliquid │   │  LLM API     │   │  External    │
   │    API      │   │ (Claude 等)   │   │   Data       │
   └─────────────┘   └──────────────┘   └──────────────┘
```

## コンポーネント詳細

### 1. データ取得レイヤー (`data_collector`)

- **役割:** Hyperliquid から市場データを定期取得し DB へ保存
- **取得データ:**
  - OHLCV（1m / 15m / 30m / 1h）
  - Funding Rate
  - HLP（Hyperliquidity Provider）データ
- **スケジューラ:** APScheduler または asyncio ベースの定期実行

### 2. 指標計算レイヤー (`indicators`)

- **役割:** 取得した生データからテクニカル指標を計算
- **指標例:**
  - EMA（指数移動平均）
  - RSI（相対力指数）
  - ATR（平均真値幅）
  - ボリンジャーバンド
  - MACD
- **出力:** AI エージェントに渡すための JSON フォーマット

### 3. AI エージェントレイヤー (`agents`)

- **役割:** 複数のAIエージェントが市場データを分析し、取引判断を下す
- **構成:** 詳細は [ai-agent-design.md](./ai-agent-design.md) 参照
- **フレームワーク:** LangChain / LangGraph

### 4. 取引実行エンジン (`executor`)

- **役割:** AIの判断を受け、Hyperliquid APIへ注文を発行
- **機能:**
  - 指値 / 成行注文
  - SL / TP 設定・更新
  - 手動トレーリングストップ（常駐プロセス）

### 5. FastAPI バックエンド

- **役割:** フロントエンドとの API 通信、各コンポーネントのオーケストレーション
- **エンドポイント:**
  - `/api/position` — 現在のポジション情報
  - `/api/logs` — AI 議論ログ
  - `/api/history` — 取引履歴
  - `/api/settings` — 設定の取得・更新

### 6. Next.js フロントエンド

- **役割:** Web ダッシュボードとしての可視化
- **主要画面:**
  - ダッシュボード（ポジション・損益確認）
  - 議論ログビューア（チャット風UI）
  - 取引履歴
  - 設定画面

## メインループ処理シーケンス

```
毎15分足の確定タイミング
        │
        ▼
  1. データ取得
     Hyperliquid API → OHLCV, FR, HLP
        │
        ▼
  2. 指標計算
     RSI, EMA, ATR 等を計算 → JSON 生成
        │
        ▼
  3. AI 合議
     3エージェントが並列分析 → マスターエージェントが最終判断
        │
        ▼
  4. 判断結果の DB 保存
     議論ログ、最終アクション
        │
        ▼
  5. 取引実行（必要な場合）
     注文発行 / ポジション更新 / SL-TP 設定
        │
        ▼
  6. 監視継続
     トレーリングストップ常駐プロセスが価格をウォッチ
```

## データベーススキーマ（概要）

```sql
-- 市場データ
market_data        (id, symbol, timeframe, timestamp, open, high, low, close, volume)
funding_rates      (id, symbol, timestamp, rate)
hlp_data           (id, timestamp, data JSON)

-- AI 関連
agent_sessions     (id, created_at, market_snapshot JSON)
agent_opinions     (id, session_id, agent_name, opinion, reasoning, action)
final_decisions    (id, session_id, action, confidence, reasoning)

-- 取引
trades             (id, session_id, symbol, side, size, entry_price, exit_price, pnl, created_at, closed_at)
trade_settings     (id, risk_percent, leverage, max_hold_hours, updated_at)
```

## セキュリティ設計

- API Key / Secret は `.env` ファイルで管理（Docker secrets または環境変数）
- DB にはシークレット情報を保存しない
- FastAPI の CORS 設定は自宅サーバー内のみに限定
