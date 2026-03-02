"""Abstract base class for LLM clients.

All LLM backends (CLI-based or API-based) implement this interface,
making it easy to swap the underlying provider without changing agent code.
"""

import json
import re
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Unified interface for LLM access, regardless of transport (CLI or API)."""

    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Send a completion request and return the raw text response.

        Args:
            system_prompt: Instructions for the model (role, output format, etc.).
            user_prompt: The actual user message / market data payload.

        Returns:
            Raw text from the model.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for this client (used in logs)."""
        ...

    @staticmethod
    def extract_json(text: str) -> dict:
        """Extract the first JSON object from LLM output.

        Handles cases where the model wraps JSON in markdown code fences,
        or includes surrounding prose.

        Raises:
            ValueError: If no valid JSON object is found.
        """
        # 1. Try ```json ... ``` or ``` ... ``` code fence
        fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence:
            return json.loads(fence.group(1))

        # 2. Find the outermost {...} block
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            return json.loads(brace_match.group(0))

        raise ValueError(f"No JSON object found in LLM output: {text[:300]!r}")
