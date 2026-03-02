"""LLM client package.

Public API:
    create_llm_client  – factory to build the configured backend
    LLMClient          – abstract base class
    MockLLMClient      – deterministic mock for tests
"""

from app.services.llm.base import LLMClient
from app.services.llm.factory import create_llm_client
from app.services.llm.mock import MockLLMClient

__all__ = ["LLMClient", "MockLLMClient", "create_llm_client"]
