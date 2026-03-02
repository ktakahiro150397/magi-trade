"""Claude Code CLI client.

Uses the `claude` CLI (Claude Code) in print mode (`-p`) for non-interactive,
single-shot completion.

Usage:
  claude -p "<prompt>"

Reference:
  https://docs.anthropic.com/en/docs/claude-code/cli-reference
"""

import logging

from app.services.llm.cli.base_cli import CLILLMClient

logger = logging.getLogger(__name__)


class ClaudeCodeCLIClient(CLILLMClient):
    """Calls the `claude` CLI with the `-p` (print) flag."""

    def __init__(
        self,
        executable: str = "claude",
        timeout: float = 120.0,
    ) -> None:
        self._executable = executable
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "claude_code_cli"

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        combined = f"{system_prompt}\n\n{user_prompt}"
        cmd = [self._executable, "-p", combined]
        logger.info("[%s] Sending prompt (%d chars)", self.name, len(combined))
        result = await self._run_command(cmd, timeout=self._timeout)
        logger.debug("[%s] Raw response: %s", self.name, result[:200])
        return result
