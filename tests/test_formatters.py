"""Tests for mypy output formatters."""

import pytest
from dr_cli.typecheck.formatters import OutputFormatter


def test_output_formatter_abc() -> None:
    """Test that OutputFormatter is an abstract base class."""
    # Cannot instantiate abstract class
    with pytest.raises(TypeError) as exc_info:
        OutputFormatter()  # type: ignore

    assert "Can't instantiate abstract class" in str(exc_info.value)

    # Test that subclass must implement format_results
    class IncompleteFormatter(OutputFormatter):
        pass

    with pytest.raises(TypeError) as exc_info:
        IncompleteFormatter()  # type: ignore

    assert "Can't instantiate abstract class" in str(exc_info.value)
