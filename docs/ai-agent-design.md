# AIエージェント設計

## 概要

3つの専門家エージェントがそれぞれの視点で市場を分析し、マスターエージェントが最終判断を下す合議制アーキテクチャを採用する。

## エージェント構成

```
┌─────────────────────────────────────────────┐
│              Market Data (JSON)             │
│    OHLCV / RSI / EMA / ATR / FR / HLP      │
└───────────────────┬─────────────────────────┘
                    │ 並列入力
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│ Trend Agent  │ │Contrarian│ │ Risk Agent  │
│  トレンド系  │ │  逆張り  │ │ リスク管理  │
└──────┬───────┘ └────┬─────┘ └──────┬──────┘
       │              │              │
       └──────────────┼──────────────┘
                      │ 意見集約
                      ▼
             ┌─────────────────┐
             │  Master Agent   │
             │    最終判断     │
             └────────┬────────┘
                      │
                      ▼
              最終アクション
         (LONG / SHORT / HOLD / CLOSE)
```

## 各エージェントの役割

### 1. Trend Agent（トレンドフォロー）

- **視点:** トレンドの方向性と強さを重視
- **参照指標:** EMA クロス、MACD、Bollinger Band
- **判断傾向:** トレンドが明確な場合に積極的にエントリーを推奨
- **プロンプト方針:**
  ```
  あなたはトレンドフォロー専門のトレーダーです。
  EMAのクロス、MACDのシグナル、価格のボリンジャーバンドに対する位置を
  重視して、現在のトレンドの方向性と強さを分析してください。
  ```

### 2. Contrarian Agent（逆張り）

- **視点:** 過熱・売られすぎのシグナルを重視
- **参照指標:** RSI、Funding Rate（過熱感）、ボリュームの異常値
- **判断傾向:** RSI 過熱・FRの極端な偏りでの反転を狙う
- **プロンプト方針:**
  ```
  あなたは逆張り専門のトレーダーです。
  RSIの過熱・売られすぎ、Funding Rateの極端な偏り、出来高の異常を重視して、
  トレンドの反転シグナルを分析してください。
  ```

### 3. Risk Agent（リスク管理）

- **視点:** ボラティリティとダウンサイドリスクを最重視
- **参照指標:** ATR、現在の Funding Rate、ポジション保有期間
- **判断傾向:** リスクが高い局面では「見送り」や「早期決済」を推奨
- **プロンプト方針:**
  ```
  あなたはリスク管理専門のトレーダーです。
  ATRによるボラティリティ、Funding Rateのコスト、ポジション保有コストを重視して、
  現在のリスクリワード比を評価してください。
  ```

### 4. Master Agent（最終判断）

- **役割:** 3エージェントの意見を統合し、最終アクションを決定
- **入力:** 各エージェントの意見 + 根拠 + 信頼度スコア
- **出力フォーマット:**
  ```json
  {
    "action": "LONG | SHORT | HOLD | CLOSE",
    "confidence": 0.0~1.0,
    "reasoning": "最終判断の根拠",
    "sl_price": 数値 (エントリー時のみ),
    "tp_price": 数値 (エントリー時のみ),
    "size_ratio": 0.0~1.0 (リスク計算後のサイズ比率)
  }
  ```

## エージェント間の合議フロー（LangGraph）

```python
# 状態定義（概念）
class TradingState(TypedDict):
    market_data: dict          # 市場データ JSON
    position: dict             # 現在のポジション
    trend_opinion: AgentOpinion
    contrarian_opinion: AgentOpinion
    risk_opinion: AgentOpinion
    final_decision: FinalDecision

# グラフ構造（概念）
graph = StateGraph(TradingState)
graph.add_node("trend_agent", trend_agent_node)
graph.add_node("contrarian_agent", contrarian_agent_node)
graph.add_node("risk_agent", risk_agent_node)
graph.add_node("master_agent", master_agent_node)

# 並列実行 → 集約
graph.add_edge(START, "trend_agent")
graph.add_edge(START, "contrarian_agent")
graph.add_edge(START, "risk_agent")
graph.add_edge("trend_agent", "master_agent")
graph.add_edge("contrarian_agent", "master_agent")
graph.add_edge("risk_agent", "master_agent")
graph.add_edge("master_agent", END)
```

## AIへの入力データ形式（JSON）

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "symbol": "BTC-PERP",
  "current_price": 45000.0,
  "timeframes": {
    "15m": {
      "ohlcv": [{"t": "...", "o": 44900, "h": 45100, "l": 44800, "c": 45000, "v": 1200}],
      "rsi": 58.3,
      "ema_short": 44950.0,
      "ema_long": 44800.0,
      "macd": {"macd": 50.2, "signal": 42.1, "hist": 8.1},
      "bb": {"upper": 45500, "mid": 45000, "lower": 44500},
      "atr": 250.0
    },
    "1h": {
      "rsi": 62.1,
      "ema_short": 44800.0,
      "ema_long": 44200.0,
      "atr": 400.0
    }
  },
  "funding_rate": {
    "current": 0.0012,
    "8h_average": 0.0008
  },
  "hlp_data": {
    "net_position": 150.0,
    "pnl_24h": 25000.0
  },
  "current_position": {
    "side": "LONG",
    "size": 0.1,
    "entry_price": 44500.0,
    "unrealized_pnl": 50.0,
    "hold_hours": 3.5
  }
}
```

## DB保存内容（議論ログ）

各エージェントセッションの以下を保存：

- セッション ID・タイムスタンプ
- 市場スナップショット（JSON）
- 各エージェントの意見・根拠・推奨アクション
- マスターエージェントの最終判断・信頼度・根拠
- 実際に実行したアクション
