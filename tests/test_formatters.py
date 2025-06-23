"""Tests for mypy output formatters."""

import pytest
from dr_cli.typecheck.formatters import OutputFormatter, TextFormatter
from dr_cli.typecheck.models import (
    MypyResults,
    MypyDiagnostic,
    Location,
    MessageLevel,
)


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


def test_text_formatter(capsys: pytest.CaptureFixture[str]) -> None:
    """Test TextFormatter outputs diagnostics and summary correctly."""
    # Create test results
    results = MypyResults(
        diagnostics=[
            MypyDiagnostic(
                location=Location(file="test.py", line=10, column=5),
                level=MessageLevel.ERROR,
                message="Test error message",
                error_code="test-error",
                notes=["This is a note", "Another note"],
            ),
            MypyDiagnostic(
                location=Location(file="other.py", line=20),
                level=MessageLevel.WARNING,
                message="Test warning",
                error_code="test-warning",
            ),
        ],
        standalone_notes=[],
        files_checked=2,
    )

    formatter = TextFormatter()
    formatter.format_results(results)

    captured = capsys.readouterr()
    output_lines = captured.out.strip().split("\n")

    # Check diagnostic output
    assert "test.py:10:5: error: Test error message [test-error]" in output_lines[0]
    assert "  note: This is a note" in output_lines[1]
    assert "  note: Another note" in output_lines[2]
    assert "other.py:20: warning: Test warning [test-warning]" in output_lines[3]

    # Check summary
    assert "Found 1 error in 1 file (checked 2 source files)" in output_lines[4]
