"""Pytest configuration and shared fixtures.

Patches the database engine at import-time so tests can run without a real
MySQL server (and without the cryptography / aiomysql native dependencies
that may not be available in the CI/test environment).
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# Stub out the database engine BEFORE any app module is imported.
# This prevents the ``create_async_engine`` call in app.core.database from
# hitting the real MySQL driver stack (aiomysql → pymysql → cryptography).
# ---------------------------------------------------------------------------

_mock_engine = MagicMock()
_mock_session_maker = MagicMock(return_value=AsyncMock())

# Pre-register stubs in sys.modules so subsequent imports get the mocks
_db_module = MagicMock()
_db_module.Base = MagicMock()
_db_module.engine = _mock_engine
_db_module.AsyncSessionLocal = _mock_session_maker
_db_module.get_db = AsyncMock()

sys.modules.setdefault("app.core.database", _db_module)

# Also stub aiomysql / pymysql / cryptography to avoid native import errors
for _mod in ("aiomysql", "pymysql", "pymysql.connections", "pymysql._auth",
             "cryptography", "cryptography.hazmat",
             "cryptography.hazmat.primitives",
             "cryptography.hazmat.primitives.serialization",
             "cryptography.hazmat.primitives.hashes"):
    sys.modules.setdefault(_mod, MagicMock())
