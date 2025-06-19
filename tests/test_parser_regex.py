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