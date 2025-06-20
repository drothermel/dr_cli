"""Mypy output parsing utilities."""

import re
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from .models import MypyDiagnostic, MypyNote, MypyResults, ParseError


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


class MypyOutputParser:
    """Parser for mypy output into structured Pydantic models."""

    def __init__(self) -> None:
        """Initialize parser with empty state."""
        self.diagnostics: list[MypyDiagnostic] = []
        self.standalone_notes: list[MypyNote] = []
        self.files_checked: int = 0
        self.current_diagnostic: MypyDiagnostic | None = None
        self.parse_errors: list[ParseError] = []

    def _try_parse_diagnostic(self, line: str) -> "MypyDiagnostic | None":
        """Try to parse a diagnostic (error/warning) line."""
        match_result = try_match_diagnostic(line)
        if not match_result:
            return None

        # Import at runtime to avoid circular imports
        from .models import Location, MessageLevel, MypyDiagnostic

        location = Location(
            file=match_result.file,
            line=match_result.line,
            column=match_result.column,
        )

        level = (
            MessageLevel.ERROR
            if match_result.level == "error"
            else MessageLevel.WARNING
        )

        return MypyDiagnostic(
            location=location,
            level=level,
            message=match_result.message,
            error_code=match_result.error_code or "",
        )

    def _try_parse_note(self, line: str) -> "MypyNote | None":
        """Try to parse a note line."""
        match_result = try_match_note(line)
        if not match_result:
            return None

        # Import at runtime to avoid circular imports
        from .models import Location, MessageLevel, MypyNote

        location = Location(
            file=match_result.file,
            line=match_result.line,
            column=match_result.column,
        )

        return MypyNote(
            location=location,
            level=MessageLevel.NOTE,
            message=match_result.message,
        )

    def _associate_note_with_diagnostic(self, note_message: str) -> None:
        """Associate a note with the current diagnostic if possible."""
        if self.current_diagnostic is not None:
            self.current_diagnostic.notes.append(note_message)

    def _try_parse_summary(self, line: str) -> bool:
        """Try to parse a summary line for file counts."""
        match = SUMMARY_PATTERN.match(line.strip())
        if not match:
            return False

        self.files_checked = int(match.group(3))
        return True

    def parse_output(self, output: str) -> "MypyResults":
        """Parse mypy output into structured results."""
        # Import at runtime to avoid circular imports
        from .models import MypyResults, ParseError

        lines = output.strip().split("\n")

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line:
                continue

            # Track if line was successfully parsed
            parsed = False

            # Try parsing as diagnostic first
            diagnostic = self._try_parse_diagnostic(line)
            if diagnostic:
                self.diagnostics.append(diagnostic)
                self.current_diagnostic = diagnostic
                parsed = True
            elif note := self._try_parse_note(line):
                # Try to associate with current diagnostic, otherwise standalone
                self._associate_note_with_diagnostic(note.message)
                if self.current_diagnostic is None:
                    self.standalone_notes.append(note)
                parsed = True
            elif self._try_parse_summary(line):
                parsed = True

            # If line wasn't parsed by any pattern, track as parse error
            if not parsed:
                self.parse_errors.append(
                    ParseError(
                        line_number=line_number,
                        line_content=raw_line,
                        reason="No pattern matched",
                    )
                )

        return MypyResults(
            diagnostics=self.diagnostics,
            standalone_notes=self.standalone_notes,
            files_checked=self.files_checked,
            parse_errors=self.parse_errors,
        )
