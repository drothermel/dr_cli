"""Mypy output parsing utilities."""

import re
from typing import NamedTuple


class MatchResult(NamedTuple):
    """Result of a regex match with typed groups."""

    file: str
    line: int
    column: int | None
    level: str
    message: str
    error_code: str | None


# Regex patterns for mypy output parsing
DIAGNOSTIC_PATTERN = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):(?:(?P<column>\d+):)?\s*"
    r"(?P<level>error|warning):\s*(?P<message>.*?)\s*"
    r"(?:\[(?P<error_code>[^\]]+)\])?$"
)

NOTE_PATTERN = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):(?:(?P<column>\d+):)?\s*"
    r"note:\s*(?P<message>.*)$"
)

SUMMARY_PATTERN = re.compile(
    r"^Found (\d+) errors? in (\d+) files? \(checked (\d+) source files?\)$"
)


def try_match_diagnostic(line: str) -> MatchResult | None:
    """Try to parse a diagnostic (error/warning) line."""
    match = DIAGNOSTIC_PATTERN.match(line.strip())
    if not match:
        return None

    return MatchResult(
        file=match.group("file"),
        line=int(match.group("line")),
        column=int(match.group("column")) if match.group("column") else None,
        level=match.group("level"),
        message=match.group("message"),
        error_code=match.group("error_code"),
    )


def try_match_note(line: str) -> MatchResult | None:
    """Try to parse a note line."""
    match = NOTE_PATTERN.match(line.strip())
    if not match:
        return None

    return MatchResult(
        file=match.group("file"),
        line=int(match.group("line")),
        column=int(match.group("column")) if match.group("column") else None,
        level="note",
        message=match.group("message"),
        error_code=None,
    )
