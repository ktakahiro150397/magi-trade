"""OpenAI Codex CLI client.

Uses the `codex` CLI (OpenAI Codex) in non-interactive / quiet mode.

Usage:
  codex --quiet "<prompt>"

Set OPENAI_API_KEY in the environment for authentication.
"""

import logging

from app.services.llm.cli.base_cli import CLILLMClient

logger = logging.getLogger(__name__)


class CodexCLIClient(CLILLMClient):
    """Calls the OpenAI `codex` CLI."""

    def __init__(
        self,
        openai_api_key: str | None = None,
        executable: str = "codex",
        timeout: float = 120.0,
    ) -> None:
        self._openai_api_key = openai_api_key
        self._executable = executable
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "codex_cli"

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        combined = f"{system_prompt}\n\n{user_prompt}"
        extra_env: dict[str, str] = {}
        if self._openai_api_key:
            extra_env["OPENAI_API_KEY"] = self._openai_api_key

        cmd = [self._executable, "--quiet", combined]
        logger.info("[%s] Sending prompt (%d chars)", self.name, len(combined))
        result = await self._run_command(cmd, extra_env=extra_env, timeout=self._timeout)
        logger.debug("[%s] Raw response: %s", self.name, result[:200])
        return result
