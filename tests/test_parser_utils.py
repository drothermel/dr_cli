"""Tests for mypy output parser utility functions."""

import pytest

from dr_cli.typecheck.parser import try_match_diagnostic, try_match_note


class TestParserUtils:
    """Test parsing utility functions."""