"""Base class for CLI-based LLM clients.

Subclasses implement `complete()` by spawning a subprocess that calls an
external CLI tool (copilot, claude, codex, gemini, etc.) and capturing stdout.
"""

import asyncio
import logging
import os

from app.services.llm.base import LLMClient

logger = logging.getLogger(__name__)


class CLILLMClient(LLMClient):
    """Executes a CLI command as a subprocess and returns its stdout."""

    async def _run_command(
        self,
        cmd: list[str],
        stdin_input: str | None = None,
        extra_env: dict[str, str] | None = None,
        timeout: float = 120.0,
    ) -> str:
        """Run *cmd* and return stdout.

        Args:
            cmd: Argv list (no shell interpolation).
            stdin_input: If provided, written to the process stdin.
            extra_env: Additional environment variables merged with the current env.
            timeout: Seconds before the subprocess is killed.

        Returns:
            Decoded stdout string.

        Raises:
            RuntimeError: On non-zero exit code or timeout.
        """
        env = {**os.environ, **(extra_env or {})}

        logger.debug("Running CLI: %s", " ".join(cmd))
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if stdin_input else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=stdin_input.encode() if stdin_input else None),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise RuntimeError(f"CLI command timed out after {timeout}s: {cmd[0]}")

        if proc.returncode != 0:
            err_text = stderr.decode(errors="replace")[:500]
            raise RuntimeError(
                f"CLI command failed (rc={proc.returncode}): {err_text}"
            )

        return stdout.decode(errors="replace")
