"""Tests for mypy output parser methods."""

import pytest

from dr_cli.typecheck.models import MessageLevel, MypyDiagnostic, MypyNote
from dr_cli.typecheck.parser import MypyOutputParser


@pytest.fixture
def parser() -> MypyOutputParser:
    """Create a fresh parser instance."""
    return MypyOutputParser()


class TestParserMethods:
    """Test parser methods that create models from parsed data."""