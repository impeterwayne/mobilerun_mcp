"""mobilerun-mcp package."""

from __future__ import annotations

import sys
import unittest.mock

# Windows compatibility: mobilerun_core imports fcntl, which is Unix-only.
if "fcntl" not in sys.modules:
    try:
        import fcntl  # noqa: F401
    except ImportError:
        sys.modules["fcntl"] = unittest.mock.MagicMock()
