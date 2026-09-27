from __future__ import annotations

import json
import sys
import unittest.mock
from pathlib import Path

if "fcntl" not in sys.modules:
    try:
        import fcntl  # noqa: F401
    except ImportError:
        sys.modules["fcntl"] = unittest.mock.MagicMock()

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_text():
    def load(name: str) -> str:
        return (FIXTURES / name).read_text()

    return load


@pytest.fixture
def state_fixture():
    def load(name: str) -> dict:
        return json.loads((FIXTURES / f"state_{name}.json").read_text())

    return load
