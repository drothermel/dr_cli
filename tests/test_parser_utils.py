"""Tests for mypy output parser utility functions."""

import pytest

from dr_cli.typecheck.parser import try_match_diagnostic, try_match_note


class TestParserUtils:
    """Test parsing utility functions."""
    
    @pytest.mark.parametrize("line,expected_file,expected_line,expected_level,expected_code", [
        ("file.py:10: error: Message [code]", "file.py", 10, "error", "code"),
        ("file.py:10:5: error: Message [code]", "file.py", 10, "error", "code"),
        ("tests/fixtures/sample_code/simple_error.py:10: error: Argument 1 to \"add_numbers\" has incompatible type \"str\"; expected \"int\"  [arg-type]",
         "tests/fixtures/sample_code/simple_error.py", 10, "error", "arg-type"),
        ("file.py:10: warning: Message", "file.py", 10, "warning", None),
    ])
    def test_try_match_diagnostic_valid_inputs(
        self, line: str, expected_file: str, expected_line: int, 
        expected_level: str, expected_code: str | None
    ) -> None:
        """Test try_match_diagnostic extracts correct fields."""
        result = try_match_diagnostic(line)
        assert result is not None
        assert result.file == expected_file
        assert result.line == expected_line
        assert result.level == expected_level
        assert result.error_code == expected_code