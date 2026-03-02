"""LLM client factory.

Select and instantiate the appropriate LLM client from a string identifier.
The identifier is read from ``settings.LLM_BACKEND`` by default, which can be
overridden in ``.env``.

Supported backends
------------------
``copilot_cli``     GitHub Copilot CLI (new standalone ``copilot`` command)
``claude_code_cli`` Claude Code CLI (``claude -p``)
``codex_cli``       OpenAI Codex CLI (``codex --quiet``)
``gemini_cli``      Google Gemini CLI (``gemini --prompt``)
``mock``            Static mock responses (testing / dry-run)
"""

import logging

from app.services.llm.base import LLMClient

logger = logging.getLogger(__name__)


def create_llm_client(backend: str | None = None) -> LLMClient:
    """Instantiate an :class:`LLMClient` for the given *backend*.

    Args:
        backend: Backend identifier.  If ``None``, reads ``settings.LLM_BACKEND``.

    Returns:
        A ready-to-use :class:`LLMClient` instance.

    Raises:
        ValueError: For unknown backend identifiers.
    """
    from app.core.config import settings

    resolved = (backend or settings.LLM_BACKEND).lower().strip()
    logger.info("Creating LLM client: backend=%s", resolved)

    if resolved == "copilot_cli":
        from app.services.llm.cli.copilot import GitHubCopilotCLIClient

        return GitHubCopilotCLIClient(
            gh_token=settings.GH_TOKEN or None,
            timeout=settings.LLM_TIMEOUT,
        )

    if resolved == "claude_code_cli":
        from app.services.llm.cli.claude_code import ClaudeCodeCLIClient

        return ClaudeCodeCLIClient(timeout=settings.LLM_TIMEOUT)

    if resolved == "codex_cli":
        from app.services.llm.cli.codex import CodexCLIClient

        return CodexCLIClient(
            openai_api_key=settings.OPENAI_API_KEY or None,
            timeout=settings.LLM_TIMEOUT,
        )

    if resolved == "gemini_cli":
        from app.services.llm.cli.gemini import GeminiCLIClient

        return GeminiCLIClient(
            google_api_key=settings.GOOGLE_API_KEY or None,
            timeout=settings.LLM_TIMEOUT,
        )

    if resolved == "mock":
        from app.services.llm.mock import MockLLMClient

        return MockLLMClient()

    raise ValueError(
        f"Unknown LLM backend: {resolved!r}. "
        "Choose from: copilot_cli, claude_code_cli, codex_cli, gemini_cli, mock"
    )
