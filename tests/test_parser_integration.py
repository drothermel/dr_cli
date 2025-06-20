"""Integration tests for mypy output parser with real output samples."""

import pytest

from dr_cli.typecheck.parser import MypyOutputParser
from tests.fixtures.mypy_output_samples import (
    SIMPLE_ERROR_OUTPUT,
    MULTIPLE_ERRORS_OUTPUT,
    MULTI_FILE_OUTPUT,
    EMPTY_OUTPUT,
    ERROR_WITH_NOTES_OVERLOAD,
)


class TestParserIntegration:
    """Test full parsing workflow with real mypy output."""

    @pytest.fixture
    def parser(self) -> MypyOutputParser:
        """Create a fresh parser instance."""
        return MypyOutputParser()

    def test_parse_simple_single_error(self, parser: MypyOutputParser) -> None:
        """Test parsing basic single error output."""
        results = parser.parse_output(SIMPLE_ERROR_OUTPUT)

        assert len(results.diagnostics) == 1
        assert results.error_count == 1
        assert results.warning_count == 0
        assert results.files_checked == 1

        error = results.diagnostics[0]
        assert error.location.file == "tests/fixtures/sample_code/simple_error.py"
        assert error.location.line == 10
        assert error.error_code == "arg-type"

    def test_parse_error_with_associated_notes(self, parser: MypyOutputParser) -> None:
        """Test parsing error with notes attached."""
        results = parser.parse_output(ERROR_WITH_NOTES_OVERLOAD)

        assert len(results.diagnostics) == 2
        assert results.files_checked == 1

        # Second error should have notes attached
        overload_error = results.diagnostics[1]
        assert overload_error.error_code == "call-overload"
        assert len(overload_error.notes) == 3
        assert "Possible overload variants:" in overload_error.notes[0]
        assert "def process(x: int) -> str" in overload_error.notes[1]
        assert "def process(x: str) -> int" in overload_error.notes[2]

    def test_parse_multiple_errors(self, parser: MypyOutputParser) -> None:
        """Test parsing multiple errors in same file."""
        results = parser.parse_output(MULTIPLE_ERRORS_OUTPUT)

        assert len(results.diagnostics) == 3
        assert results.error_count == 3
        assert results.warning_count == 0
        assert results.files_checked == 1

        # Check error types
        assert results.diagnostics[0].error_code == "name-defined"
        assert results.diagnostics[1].error_code == "assignment"
        assert results.diagnostics[2].error_code == "arg-type"

        # All from same file
        assert all(
            d.location.file == "tests/fixtures/sample_code/multiple_errors.py"
            for d in results.diagnostics
        )

    def test_parse_multi_file_output(self, parser: MypyOutputParser) -> None:
        """Test parsing errors across multiple files."""
        results = parser.parse_output(MULTI_FILE_OUTPUT)

        assert len(results.diagnostics) == 1
        assert results.error_count == 1
        assert results.files_checked == 2  # Checked 2 files

        error = results.diagnostics[0]
        assert (
            error.location.file
            == "tests/fixtures/sample_code/multi_file_project/file_a.py"
        )
        assert error.error_code == "arg-type"

        # Important: only 1 file had errors even though 2 were checked
        assert len(results.files_with_errors) == 1

    def test_parse_empty_output(self, parser: MypyOutputParser) -> None:
        """Test parsing when no errors found."""
        results = parser.parse_output(EMPTY_OUTPUT)

        assert len(results.diagnostics) == 0
        assert results.error_count == 0
        assert results.warning_count == 0
        # Success messages don't update files_checked currently
        assert results.files_checked == 0
        assert len(results.files_with_errors) == 0

    def test_parse_malformed_lines(self, parser: MypyOutputParser) -> None:
        """Test parser handles malformed lines gracefully."""
        malformed = """
        Random text that doesn't match
        tests/file.py: missing line number
        10: missing filename
        tests/file.py:10: error: Valid error line [code]
        More random text
        Found 1 error in 1 file (checked 1 source file)
        """
        results = parser.parse_output(malformed)

        # Should only parse the valid error line
        assert len(results.diagnostics) == 1
        assert results.diagnostics[0].error_code == "code"
