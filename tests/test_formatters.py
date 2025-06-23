"""Tests for mypy output formatters."""

import json
from pathlib import Path

import pytest
from dr_cli.typecheck.formatters import OutputFormatter, TextFormatter, JsonlFormatter
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


def test_jsonl_formatter_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """Test JsonlFormatter outputs errors as JSONL to stdout."""
    # Create test results with errors and warnings
    results = MypyResults(
        diagnostics=[
            MypyDiagnostic(
                location=Location(file="test.py", line=10, column=5),
                level=MessageLevel.ERROR,
                message="First error",
                error_code="error-1",
            ),
            MypyDiagnostic(
                location=Location(file="other.py", line=20),
                level=MessageLevel.WARNING,
                message="A warning",
                error_code="warn-1",
            ),
            MypyDiagnostic(
                location=Location(file="test.py", line=30),
                level=MessageLevel.ERROR,
                message="Second error",
                error_code="error-2",
            ),
        ],
        standalone_notes=[],
        files_checked=2,
    )

    formatter = JsonlFormatter()
    formatter.format_results(results)

    captured = capsys.readouterr()
    output_lines = captured.out.strip().split("\n")

    # Should have 2 lines (errors only)
    assert len(output_lines) == 2

    # Parse and verify first error
    first_error = json.loads(output_lines[0])
    assert first_error["file"] == "test.py"
    assert first_error["line"] == 10
    assert first_error["column"] == 5
    assert first_error["level"] == "error"
    assert first_error["message"] == "First error"
    assert first_error["error_code"] == "error-1"

    # Parse and verify second error
    second_error = json.loads(output_lines[1])
    assert second_error["file"] == "test.py"
    assert second_error["line"] == 30
    assert second_error["level"] == "error"
    assert second_error["message"] == "Second error"
    assert second_error["error_code"] == "error-2"


def test_jsonl_formatter_file_output(tmp_path: Path) -> None:
    """Test JsonlFormatter writes errors to file when output_path provided."""
    # Create test results
    results = MypyResults(
        diagnostics=[
            MypyDiagnostic(
                location=Location(file="test.py", line=10),
                level=MessageLevel.ERROR,
                message="Test error",
                error_code="test-error",
            ),
        ],
        standalone_notes=[],
        files_checked=1,
    )

    output_file = tmp_path / "errors.jsonl"
    formatter = JsonlFormatter()
    formatter.format_results(results, str(output_file))

    # Verify file was created and contains expected content
    assert output_file.exists()
    lines = output_file.read_text().strip().split("\n")

    # Should have metadata line + one error line
    assert len(lines) == 2

    # First line should be metadata
    metadata = json.loads(lines[0])
    assert metadata["type"] == "metadata"
    assert metadata["error_count"] == 1

    # Second line should be error
    error_data = json.loads(lines[1])
    assert error_data["file"] == "test.py"
    assert error_data["line"] == 10
    assert error_data["level"] == "error"


def test_jsonl_metadata(tmp_path: Path) -> None:
    """Test JSONL error count metadata."""
    # Create results with multiple errors
    diagnostics = [
        MypyDiagnostic(
            location=Location(file="test1.py", line=1),
            level=MessageLevel.ERROR,
            message="Error 1",
            error_code="test",
        ),
        MypyDiagnostic(
            location=Location(file="test2.py", line=2),
            level=MessageLevel.ERROR,
            message="Error 2",
            error_code="test",
        ),
    ]

    results = MypyResults(diagnostics=diagnostics, standalone_notes=[], files_checked=2)
    formatter = JsonlFormatter()

    # Test with temp file
    output_file = tmp_path / "test_metadata.jsonl"
    formatter.format_results(results, str(output_file))

    # Read and verify metadata
    lines = output_file.read_text().strip().split("\n")

    # Should have metadata + 2 errors
    assert len(lines) == 3
    metadata = json.loads(lines[0])
    assert metadata["error_count"] == 2
