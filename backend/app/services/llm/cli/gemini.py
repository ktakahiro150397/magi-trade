"""Google Gemini CLI client.

Uses the `gemini` CLI (Google Gemini) in non-interactive mode.

Usage:
  gemini --prompt "<text>"   (or pipe via stdin)

Set GOOGLE_API_KEY (or GEMINI_API_KEY) in the environment.
"""

import logging

from app.services.llm.cli.base_cli import CLILLMClient

logger = logging.getLogger(__name__)


class GeminiCLIClient(CLILLMClient):
    """Calls the Google `gemini` CLI."""

    def __init__(
        self,
        google_api_key: str | None = None,
        executable: str = "gemini",
        timeout: float = 120.0,
    ) -> None:
        self._google_api_key = google_api_key
        self._executable = executable
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "gemini_cli"

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        combined = f"{system_prompt}\n\n{user_prompt}"
        extra_env: dict[str, str] = {}
        if self._google_api_key:
            extra_env["GOOGLE_API_KEY"] = self._google_api_key

        # Gemini CLI accepts the prompt via stdin or --prompt flag
        cmd = [self._executable, "--prompt", combined]
        logger.info("[%s] Sending prompt (%d chars)", self.name, len(combined))
        result = await self._run_command(cmd, extra_env=extra_env, timeout=self._timeout)
        logger.debug("[%s] Raw response: %s", self.name, result[:200])
        return result
