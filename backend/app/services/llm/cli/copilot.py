"""GitHub Copilot CLI client.

Uses the **new standalone** GitHub Copilot CLI (`copilot` command) which
replaced the deprecated `gh copilot` extension (deprecated Oct 2025).

Reference:
  https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli

Non-interactive invocation:
  copilot --prompt "<text>" --allow-all-tools --allow-all-paths

Authentication:
  Set GH_TOKEN (fine-grained PAT with "Copilot Requests" permission) in the
  environment or in the application settings.
"""

import logging

from app.services.llm.cli.base_cli import CLILLMClient

logger = logging.getLogger(__name__)


class GitHubCopilotCLIClient(CLILLMClient):
    """Calls the standalone `copilot` CLI in non-interactive mode."""

    def __init__(
        self,
        gh_token: str | None = None,
        executable: str = "copilot",
        timeout: float = 120.0,
    ) -> None:
        """
        Args:
            gh_token: GitHub PAT with Copilot access.  Exposed as GH_TOKEN.
            executable: Path or name of the copilot binary.  Override when the
                        binary lives outside PATH.
            timeout: Seconds to wait for a response before killing the process.
        """
        self._gh_token = gh_token
        self._executable = executable
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "github_copilot_cli"

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Combine system + user prompts and send to `copilot --prompt`.

        The combined text is passed via the ``--prompt`` flag so the process
        runs headlessly without interactive TTY input.
        """
        combined = f"{system_prompt}\n\n{user_prompt}"

        extra_env: dict[str, str] = {}
        if self._gh_token:
            extra_env["GH_TOKEN"] = self._gh_token

        # --allow-all-tools / --allow-all-paths suppress confirmation prompts
        cmd = [
            self._executable,
            "--prompt",
            combined,
            "--allow-all-tools",
            "--allow-all-paths",
        ]

        logger.info("[%s] Sending prompt (%d chars)", self.name, len(combined))
        result = await self._run_command(
            cmd,
            extra_env=extra_env,
            timeout=self._timeout,
        )
        logger.debug("[%s] Raw response: %s", self.name, result[:200])
        return result
