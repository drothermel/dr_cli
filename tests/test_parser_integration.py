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
        malformed = """Random text that doesn't match
tests/file.py: missing line number
10: missing filename
tests/file.py:10: error: Valid error line [code]
More random text
Found 1 error in 1 file (checked 1 source file)"""
        results = parser.parse_output(malformed)

        # Should only parse the valid error line
        assert len(results.diagnostics) == 1
        assert results.diagnostics[0].error_code == "code"

        # Should track unparseable lines as parse errors
        assert len(results.parse_errors) == 4
        # Line 1: "Random text that doesn't match"
        assert results.parse_errors[0].line_number == 1
        assert "Random text" in results.parse_errors[0].line_content
        # Line 2: "tests/file.py: missing line number"
        assert results.parse_errors[1].line_number == 2
        assert "missing line number" in results.parse_errors[1].line_content
        # Line 3: "10: missing filename"
        assert results.parse_errors[2].line_number == 3
        assert "missing filename" in results.parse_errors[2].line_content
        # Line 5: "More random text"
        assert results.parse_errors[3].line_number == 5
        assert "More random text" in results.parse_errors[3].line_content
        # All should have the same reason
        for error in results.parse_errors:
            assert error.reason == "No pattern matched"

    def test_parse_errors_not_created_for_valid_lines(
        self, parser: MypyOutputParser
    ) -> None:
        """Test that successfully parsed lines don't create parse errors."""
        results = parser.parse_output(SIMPLE_ERROR_OUTPUT)

        # Should have parsed the error and summary
        assert len(results.diagnostics) == 1
        assert results.files_checked == 1

        # No parse errors for valid output
        assert len(results.parse_errors) == 0

    def test_debug_mode_prints_messages(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that debug mode prints debug messages."""
        from dr_cli.typecheck.parser import ParserConfig

        config = ParserConfig(debug=True)
        parser = MypyOutputParser(config=config)

        output = """tests/file.py:10: error: Test error [code]
tests/file.py:10: note: Test note
Unknown line
Found 1 error in 1 file (checked 1 source file)"""

        results = parser.parse_output(output)

        # Check that parsing worked
        assert len(results.diagnostics) == 1
        assert len(results.parse_errors) == 1

        # Check debug output
        captured = capsys.readouterr()
        assert "[DEBUG] Line 1: Parsed as diagnostic" in captured.out
        assert "[DEBUG] Line 2: Parsed as note" in captured.out
        assert "[DEBUG] Line 3: No pattern matched" in captured.out
        assert "[DEBUG] Line 4: Parsed as summary" in captured.out

    def test_parser_with_custom_config(self) -> None:
        """Test parser with custom configuration."""
        from dr_cli.typecheck.parser import ParserConfig

        # Test with column numbers disabled (though this doesn't affect parsing yet)
        config = ParserConfig(show_column_numbers=False, show_error_end=True)
        parser = MypyOutputParser(config=config)

        # Should still parse normally
        results = parser.parse_output(SIMPLE_ERROR_OUTPUT)
        assert len(results.diagnostics) == 1

        # Config should be stored
        assert parser.config.show_column_numbers is False
        assert parser.config.show_error_end is True
        assert parser.config.debug is False

    def test_parser_with_custom_regex_patterns(self) -> None:
        """Test parser with custom regex patterns."""
        import re
        from dr_cli.typecheck.parser import ParserConfig

        # Custom pattern that expects different format
        # e.g., "ERROR in file.py at 10: message"
        custom_diagnostic = re.compile(
            r"^(?P<level>ERROR|WARNING) in (?P<file>[^:]+) "
            r"at (?P<line>\d+): (?P<message>.*)$"
        )

        config = ParserConfig(custom_diagnostic_pattern=custom_diagnostic)
        parser = MypyOutputParser(config=config)

        custom_output = """ERROR in test.py at 42: Something went wrong
Found 1 error in 1 file (checked 1 source file)"""

        results = parser.parse_output(custom_output)

        # Should parse with custom pattern
        assert len(results.diagnostics) == 1
        diagnostic = results.diagnostics[0]
        assert diagnostic.location.file == "test.py"
        assert diagnostic.location.line == 42
        assert diagnostic.message == "Something went wrong"
        assert diagnostic.level.value == "error"  # Normalized to lowercase

    def test_create_with_minimal_output(self) -> None:
        """Test creating parser with minimal output configuration."""
        parser = MypyOutputParser.create_with_minimal_output()

        assert parser.config.show_column_numbers is False
        assert parser.config.show_error_end is False

        # Should still parse normal output
        results = parser.parse_output(SIMPLE_ERROR_OUTPUT)
        assert len(results.diagnostics) == 1

    def test_create_with_full_output(self) -> None:
        """Test creating parser with full output configuration."""
        parser = MypyOutputParser.create_with_full_output()

        assert parser.config.show_column_numbers is True
        assert parser.config.show_error_end is True

        # Should still parse normal output
        results = parser.parse_output(SIMPLE_ERROR_OUTPUT)
        assert len(results.diagnostics) == 1

    def test_detect_format_with_columns(self) -> None:
        """Test format detection with column numbers."""
        sample = """file.py:10:5: error: Message [code]
file2.py:20:3: warning: Another message"""

        config = MypyOutputParser.detect_format(sample)
        assert config.show_column_numbers is True

    def test_detect_format_without_columns(self) -> None:
        """Test format detection without column numbers."""
        sample = """file.py:10: error: Message [code]
file2.py:20: warning: Another message"""

        config = MypyOutputParser.detect_format(sample)
        assert config.show_column_numbers is False
