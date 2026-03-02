"""Mock LLM client for unit tests and local dry-runs.

Returns pre-configured JSON responses without calling any external process,
making tests fast and deterministic.
"""

import json
import logging

from app.services.llm.base import LLMClient

logger = logging.getLogger(__name__)

# Default mock responses (valid JSON that agents can parse)
_DEFAULT_AGENT_RESPONSE = json.dumps(
    {
        "action": "HOLD",
        "confidence": 0.65,
        "reasoning": (
            "モック応答: 市場データを分析した結果、現在は明確なトレンドが見られないため"
            "様子見 (HOLD) が適切と判断します。"
        ),
    }
)

_DEFAULT_MASTER_RESPONSE = json.dumps(
    {
        "action": "HOLD",
        "confidence": 0.70,
        "reasoning": (
            "モック応答: 3エージェントの合議の結果、HOLDが最適と判断。"
            "トレンドエージェントとリスクエージェントの見解が一致しています。"
        ),
        "sl_price": None,
        "tp_price": None,
        "size_ratio": None,
    }
)


class MockLLMClient(LLMClient):
    """Returns configurable static responses for testing.

    Args:
        responses: Optional dict mapping keyword → JSON string.
                   Keys ``"master"`` and ``"default"`` are checked against the
                   system prompt to select the appropriate response.
        fixed_response: If provided, always return this string regardless of
                        the prompt content (useful for simple unit tests).
    """

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        fixed_response: str | None = None,
    ) -> None:
        self._responses = responses or {}
        self._fixed_response = fixed_response

    @property
    def name(self) -> str:
        return "mock"

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        if self._fixed_response is not None:
            logger.debug("[mock] Returning fixed response")
            return self._fixed_response

        combined = (system_prompt + user_prompt).lower()

        if "master" in combined:
            response = self._responses.get("master", _DEFAULT_MASTER_RESPONSE)
        else:
            response = self._responses.get("default", _DEFAULT_AGENT_RESPONSE)

        logger.debug("[mock] Returning response for prompt type (master=%s)", "master" in combined)
        return response
