"""Tests for mypy output parser regex patterns."""

import re

import pytest

from dr_cli.typecheck.parser import DIAGNOSTIC_PATTERN, NOTE_PATTERN, SUMMARY_PATTERN


def assert_pattern_matches(pattern: re.Pattern[str], text: str) -> re.Match[str]:
    """Assert pattern matches and return match object."""
    match = pattern.match(text)
    assert match is not None, f"Pattern should match: {text}"
    return match


def assert_pattern_not_matches(pattern: re.Pattern[str], text: str) -> None:
    """Assert pattern does not match."""
    match = pattern.match(text)
    assert match is None, f"Pattern should not match: {text}"


# Parametrized test data for diagnostic pattern
VALID_DIAGNOSTIC_LINES = [
    "file.py:10: error: Message [code]",
    "file.py:10:5: error: Message [code]",
    "path/to/file.py:10: warning: Message [code]",
    "file.py:10: error: Message without code",
]

INVALID_DIAGNOSTIC_LINES = [
    "file.py:10: note: This is a note",
    "file.py: error: Missing line number",
    "10: error: Missing filename",
    "Not a diagnostic line at all",
]


@pytest.mark.parametrize("line", [
    "file.py:10: error: Message [code]",
    "file.py:10:5: error: Message [code]",
    "tests/fixtures/sample_code/simple_error.py:10: error: Argument 1 to \"add_numbers\" has incompatible type \"str\"; expected \"int\"  [arg-type]",
    "file.py:10: error: Message without code",
])
def test_diagnostic_pattern_matches_valid_error_lines(line: str) -> None:
    """Test that diagnostic pattern matches valid error lines."""
    match = assert_pattern_matches(DIAGNOSTIC_PATTERN, line)
    assert match.group("level") == "error"


@pytest.mark.parametrize("line", [
    "file.py:10: warning: Message [code]",
    "file.py:10:5: warning: Message [code]",
    "path/to/file.py:10: warning: Unused variable 'x'  [unused-var]",
    "file.py:10: warning: Message without code",
])
def test_diagnostic_pattern_matches_valid_warning_lines(line: str) -> None:
    """Test that diagnostic pattern matches valid warning lines."""
    match = assert_pattern_matches(DIAGNOSTIC_PATTERN, line)
    assert match.group("level") == "warning"


@pytest.mark.parametrize("line", [
    "file.py:10: note: This is a note",
    "file.py: error: Missing line number",
    "10: error: Missing filename",
    "Not a diagnostic line at all",
    "file.py:10 error: Missing colon",
    "file.py:10: info: Wrong level",
])
def test_diagnostic_pattern_rejects_invalid_lines(line: str) -> None:
    """Test that diagnostic pattern rejects invalid lines."""
    assert_pattern_not_matches(DIAGNOSTIC_PATTERN, line)


@pytest.mark.parametrize("line", [
    "file.py:10: note: This is a note",
    "file.py:10:5: note: This is a note with column",
    "path/to/file.py:10: note: See reference implementation",
    "file.py:10: note: Possible overload variants:",
])
def test_note_pattern_matches_valid_note_lines(line: str) -> None:
    """Test that note pattern matches valid note lines."""
    match = assert_pattern_matches(NOTE_PATTERN, line)
    assert match.group("message") is not None
    assert match.group("file") is not None


@pytest.mark.parametrize("line", [
    "file.py:10: error: This is not a note",
    "file.py: note: Missing line number",
    "10: note: Missing filename",
    "file.py:10 note: Missing colon",
])
def test_note_pattern_rejects_invalid_lines(line: str) -> None:
    """Test that note pattern rejects invalid lines."""
    assert_pattern_not_matches(NOTE_PATTERN, line)


@pytest.mark.parametrize("line,expected_errors,expected_files,expected_checked", [
    ("Found 1 error in 1 file (checked 1 source file)", 1, 1, 1),
    ("Found 2 errors in 1 file (checked 1 source file)", 2, 1, 1),
    ("Found 1 error in 2 files (checked 3 source files)", 1, 2, 3),
    ("Found 3 errors in 2 files (checked 5 source files)", 3, 2, 5),
])
def test_summary_pattern_matches_valid_summary_lines(
    line: str, expected_errors: int, expected_files: int, expected_checked: int
) -> None:
    """Test that summary pattern matches and extracts correct values."""
    match = assert_pattern_matches(SUMMARY_PATTERN, line)
    assert int(match.group(1)) == expected_errors
    assert int(match.group(2)) == expected_files
    assert int(match.group(3)) == expected_checked