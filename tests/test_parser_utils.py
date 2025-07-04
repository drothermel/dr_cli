"""Tests for mypy output parser utility functions."""

import pytest

from dr_cli.typecheck.parser import try_match_diagnostic, try_match_note


class TestParserUtils:
    """Test parsing utility functions."""

    @pytest.mark.parametrize(
        ("line", "expected_file", "expected_line", "expected_level", "expected_code"),
        [
            ("file.py:10: error: Message [code]", "file.py", 10, "error", "code"),
            ("file.py:10:5: error: Message [code]", "file.py", 10, "error", "code"),
            (
                'tests/fixtures/sample_code/simple_error.py:10: error: Argument 1 to "add_numbers" has incompatible type "str"; expected "int"  [arg-type]',  # noqa: E501
                "tests/fixtures/sample_code/simple_error.py",
                10,
                "error",
                "arg-type",
            ),
            ("file.py:10: warning: Message", "file.py", 10, "warning", None),
        ],
    )
    def test_try_match_diagnostic_valid_inputs(
        self,
        line: str,
        expected_file: str,
        expected_line: int,
        expected_level: str,
        expected_code: str | None,
    ) -> None:
        """Test try_match_diagnostic extracts correct fields."""
        result = try_match_diagnostic(line)
        assert result is not None
        assert result.file == expected_file
        assert result.line == expected_line
        assert result.level == expected_level
        assert result.error_code == expected_code

    @pytest.mark.parametrize(
        ("line", "expected_file", "expected_line", "expected_column"),
        [
            ("file.py:10: note: This is a note", "file.py", 10, None),
            ("file.py:10:5: note: This is a note with column", "file.py", 10, 5),
            (
                "path/to/file.py:10: note: See reference implementation",
                "path/to/file.py",
                10,
                None,
            ),
        ],
    )
    def test_try_match_note_valid_inputs(
        self,
        line: str,
        expected_file: str,
        expected_line: int,
        expected_column: int | None,
    ) -> None:
        """Test try_match_note extracts correct fields."""
        result = try_match_note(line)
        assert result is not None
        assert result.file == expected_file
        assert result.line == expected_line
        assert result.column == expected_column
        assert result.level == "note"

    @pytest.mark.parametrize(
        "line",
        [
            "file.py:10: note: This is a note",  # Wrong function - note not diagnostic
            "file.py: error: Missing line number",
            "10: error: Missing filename",
            "Not a diagnostic line at all",
        ],
    )
    def test_try_match_diagnostic_invalid_inputs(self, line: str) -> None:
        """Test try_match_diagnostic returns None for invalid inputs."""
        result = try_match_diagnostic(line)
        assert result is None

    @pytest.mark.parametrize(
        "line",
        [
            "file.py:10: error: This is not a note",  # Wrong function - error not note
            "file.py: note: Missing line number",
            "10: note: Missing filename",
            "Random text without pattern",
        ],
    )
    def test_try_match_note_invalid_inputs(self, line: str) -> None:
        """Test try_match_note returns None for invalid inputs."""
        result = try_match_note(line)
        assert result is None
