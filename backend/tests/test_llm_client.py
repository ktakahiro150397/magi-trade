"""Unit tests for LLM client implementations.

All tests use MockLLMClient or test LLMClient.extract_json directly —
no external processes or APIs are called.
"""

import json

import pytest

from app.services.llm.base import LLMClient
from app.services.llm.mock import MockLLMClient


# ---------------------------------------------------------------------------
# extract_json
# ---------------------------------------------------------------------------


class TestExtractJson:
    def test_plain_json(self):
        text = '{"action": "HOLD", "confidence": 0.6, "reasoning": "test"}'
        result = LLMClient.extract_json(text)
        assert result["action"] == "HOLD"
        assert result["confidence"] == 0.6

    def test_json_in_code_fence(self):
        text = 'Here is my answer:\n```json\n{"action": "LONG", "confidence": 0.8, "reasoning": "uptrend"}\n```'
        result = LLMClient.extract_json(text)
        assert result["action"] == "LONG"

    def test_json_in_unlabelled_code_fence(self):
        text = '```\n{"action": "SHORT", "confidence": 0.7, "reasoning": "overbought"}\n```'
        result = LLMClient.extract_json(text)
        assert result["action"] == "SHORT"

    def test_json_with_surrounding_text(self):
        text = 'After analysis, I recommend:\n{"action": "CLOSE", "confidence": 0.9, "reasoning": "risk too high"}\nThank you.'
        result = LLMClient.extract_json(text)
        assert result["action"] == "CLOSE"

    def test_no_json_raises(self):
        with pytest.raises(ValueError, match="No JSON"):
            LLMClient.extract_json("No JSON here at all.")


# ---------------------------------------------------------------------------
# MockLLMClient
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestMockLLMClient:
    async def test_default_response_is_hold(self):
        client = MockLLMClient()
        response = await client.complete("You are a trend agent.", "Analyse BTC")
        parsed = LLMClient.extract_json(response)
        assert parsed["action"] == "HOLD"

    async def test_master_response_detected_by_keyword(self):
        client = MockLLMClient()
        # "master" keyword in system prompt → master response
        response = await client.complete("You are a master agent.", "Aggregate opinions")
        parsed = LLMClient.extract_json(response)
        # Master response includes sl_price / tp_price keys
        assert "sl_price" in parsed

    async def test_fixed_response_overrides_everything(self):
        fixed = json.dumps({"action": "LONG", "confidence": 1.0, "reasoning": "fixed"})
        client = MockLLMClient(fixed_response=fixed)
        response = await client.complete("system", "user")
        assert response == fixed

    async def test_custom_responses_dict(self):
        custom = json.dumps({"action": "SHORT", "confidence": 0.99, "reasoning": "custom"})
        client = MockLLMClient(responses={"default": custom})
        response = await client.complete("You are a trend agent.", "Analyse")
        parsed = LLMClient.extract_json(response)
        assert parsed["action"] == "SHORT"
        assert parsed["confidence"] == 0.99

    async def test_name_property(self):
        client = MockLLMClient()
        assert client.name == "mock"


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


class TestCreateLlmClient:
    def test_create_mock(self, monkeypatch):
        monkeypatch.setenv("LLM_BACKEND", "mock")
        from app.services.llm.factory import create_llm_client

        client = create_llm_client("mock")
        assert isinstance(client, MockLLMClient)

    def test_unknown_backend_raises(self):
        from app.services.llm.factory import create_llm_client

        with pytest.raises(ValueError, match="Unknown LLM backend"):
            create_llm_client("unsupported_backend")

    def test_create_copilot_cli(self):
        from app.services.llm.cli.copilot import GitHubCopilotCLIClient
        from app.services.llm.factory import create_llm_client

        client = create_llm_client("copilot_cli")
        assert isinstance(client, GitHubCopilotCLIClient)
        assert client.name == "github_copilot_cli"

    def test_create_claude_code_cli(self):
        from app.services.llm.cli.claude_code import ClaudeCodeCLIClient
        from app.services.llm.factory import create_llm_client

        client = create_llm_client("claude_code_cli")
        assert isinstance(client, ClaudeCodeCLIClient)
        assert client.name == "claude_code_cli"

    def test_create_codex_cli(self):
        from app.services.llm.cli.codex import CodexCLIClient
        from app.services.llm.factory import create_llm_client

        client = create_llm_client("codex_cli")
        assert isinstance(client, CodexCLIClient)
        assert client.name == "codex_cli"

    def test_create_gemini_cli(self):
        from app.services.llm.cli.gemini import GeminiCLIClient
        from app.services.llm.factory import create_llm_client

        client = create_llm_client("gemini_cli")
        assert isinstance(client, GeminiCLIClient)
        assert client.name == "gemini_cli"
