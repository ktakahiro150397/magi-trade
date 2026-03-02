"""Prompt templates for each AI agent.

Each template is a callable that accepts a market data dict and returns a
(system_prompt, user_prompt) tuple ready to pass to an LLMClient.

Output format required from ALL agents:
    ```json
    {
      "action": "LONG" | "SHORT" | "HOLD" | "CLOSE",
      "confidence": <float 0.0-1.0>,
      "reasoning": "<Japanese explanation>"
    }
    ```

The Master Agent additionally outputs sl_price, tp_price, size_ratio.
"""

import json

_JSON_FORMAT = """
必ず以下の JSON 形式のみで回答してください。余計な説明やマークダウンは不要です。
```json
{
  "action": "LONG" または "SHORT" または "HOLD" または "CLOSE",
  "confidence": 0.0〜1.0,
  "reasoning": "判断理由（日本語）"
}
```
""".strip()

_MASTER_JSON_FORMAT = """
必ず以下の JSON 形式のみで回答してください。余計な説明やマークダウンは不要です。
```json
{
  "action": "LONG" または "SHORT" または "HOLD" または "CLOSE",
  "confidence": 0.0〜1.0,
  "reasoning": "最終判断の理由（日本語）",
  "sl_price": <エントリー時はストップロス価格(数値)、それ以外は null>,
  "tp_price": <エントリー時はテイクプロフィット価格(数値)、それ以外は null>,
  "size_ratio": <0.0〜1.0 のポジションサイズ比率、HOLD/CLOSE は null>
}
```
""".strip()


def trend_agent_prompts(market_data: dict) -> tuple[str, str]:
    system = f"""あなたはトレンドフォロー専門の仮想通貨トレーダーです。
EMA のクロス、MACD のシグナル、価格のボリンジャーバンドに対する位置を重視して
現在のトレンドの方向性と強さを分析し、エントリー方向を判断してください。

{_JSON_FORMAT}"""

    user = f"""以下の市場データを分析してください:
{json.dumps(market_data, ensure_ascii=False, indent=2)}"""

    return system, user


def contrarian_agent_prompts(market_data: dict) -> tuple[str, str]:
    system = f"""あなたは逆張り専門の仮想通貨トレーダーです。
RSI の過熱・売られすぎ、Funding Rate の極端な偏り、出来高の異常を重視して
トレンドの反転シグナルを分析し、エントリー方向を判断してください。

{_JSON_FORMAT}"""

    user = f"""以下の市場データを分析してください:
{json.dumps(market_data, ensure_ascii=False, indent=2)}"""

    return system, user


def risk_agent_prompts(market_data: dict) -> tuple[str, str]:
    system = f"""あなたはリスク管理専門の仮想通貨トレーダーです。
ATR によるボラティリティ、Funding Rate のコスト、ポジション保有コストを重視して
現在のリスクリワード比を評価してください。
リスクが高い局面では HOLD (様子見) を推奨してください。

{_JSON_FORMAT}"""

    user = f"""以下の市場データを分析してください:
{json.dumps(market_data, ensure_ascii=False, indent=2)}"""

    return system, user


def master_agent_prompts(
    market_data: dict,
    trend_opinion: dict,
    contrarian_opinion: dict,
    risk_opinion: dict,
) -> tuple[str, str]:
    system = f"""あなたはマスタートレーダーです。
3名の専門エージェント（トレンド、逆張り、リスク）の意見を統合し
最終的な取引アクションを決定してください。

判断基準:
- 3エージェントの多数決を基本とする
- リスクエージェントが HOLD を推奨する場合はリスクを最優先する
- 信頼度スコアを加重して最終的な confidence を算出する

{_MASTER_JSON_FORMAT}"""

    user = f"""市場データ:
{json.dumps(market_data, ensure_ascii=False, indent=2)}

トレンドエージェントの意見:
{json.dumps(trend_opinion, ensure_ascii=False, indent=2)}

逆張りエージェントの意見:
{json.dumps(contrarian_opinion, ensure_ascii=False, indent=2)}

リスクエージェントの意見:
{json.dumps(risk_opinion, ensure_ascii=False, indent=2)}"""

    return system, user
