"""Mypy output parsing utilities."""

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from .models import MypyDiagnostic, MypyNote, MypyResults, ParseError


@dataclass
class ParserConfig:
    """Configuration for mypy output parser.

    Attributes:
        show_column_numbers: Whether mypy includes column numbers in output.
        show_error_end: Whether mypy shows end line/column for errors.
        debug: Whether to print debug messages during parsing.
        custom_diagnostic_pattern: Custom regex pattern for diagnostics.
        custom_note_pattern: Custom regex pattern for notes.
        custom_summary_pattern: Custom regex pattern for summary lines.
    """

    show_column_numbers: bool = True
    show_error_end: bool = False
    debug: bool = False
    custom_diagnostic_pattern: re.Pattern[str] | None = None
    custom_note_pattern: re.Pattern[str] | None = None
    custom_summary_pattern: re.Pattern[str] | None = None


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

    def __init__(self, config: ParserConfig | None = None) -> None:
        """Initialize parser with empty state.

        Args:
            config: Parser configuration. If None, uses default config.
        """
        self.config = config or ParserConfig()
        self.diagnostics: list[MypyDiagnostic] = []
        self.standalone_notes: list[MypyNote] = []
        self.files_checked: int = 0
        self.current_diagnostic: MypyDiagnostic | None = None
        self.parse_errors: list[ParseError] = []

    @classmethod
    def create_with_minimal_output(cls) -> "MypyOutputParser":
        """Create parser for mypy with minimal output (no columns)."""
        config = ParserConfig(show_column_numbers=False)
        return cls(config)

    @classmethod
    def create_with_full_output(cls) -> "MypyOutputParser":
        """Create parser for mypy with full output including end positions."""
        config = ParserConfig(show_column_numbers=True, show_error_end=True)
        return cls(config)

    @classmethod
    def detect_format(cls, sample_output: str) -> ParserConfig:
        """Attempt to detect mypy output format from a sample.

        Args:
            sample_output: Sample mypy output to analyze.

        Returns:
            ParserConfig with detected settings.
        """
        config = ParserConfig()

        # Check for column numbers (e.g., "file.py:10:5: error:")
        # Match pattern with file:line:column: level
        if re.search(r'\S+:\d+:\d+:\s*(error|warning)', sample_output):
            config.show_column_numbers = True
        else:
            config.show_column_numbers = False

        # Check for end positions (rare in standard mypy output)
        # Would need specific patterns if mypy adds this feature

        return config

    def _try_parse_diagnostic(self, line: str) -> "MypyDiagnostic | None":
        """Try to parse a diagnostic (error/warning) line."""
        # Use custom pattern if provided
        if self.config.custom_diagnostic_pattern:
            match = self.config.custom_diagnostic_pattern.match(line.strip())
            if match:
                # Extract from custom pattern - assumes same group names
                # Get optional groups safely
                groupdict = match.groupdict()
                column_val = groupdict.get("column")
                error_code = groupdict.get("error_code")

                match_result = MatchResult(
                    file=match.group("file"),
                    line=int(match.group("line")),
                    column=int(column_val) if column_val else None,
                    level=match.group("level").lower(),  # Normalize to lowercase
                    message=match.group("message"),
                    error_code=error_code,
                )
            else:
                return None
        else:
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
        # Use custom pattern if provided
        if self.config.custom_note_pattern:
            match = self.config.custom_note_pattern.match(line.strip())
            if match:
                # Get optional groups safely
                column_val = match.groupdict().get("column")

                match_result = MatchResult(
                    file=match.group("file"),
                    line=int(match.group("line")),
                    column=int(column_val) if column_val else None,
                    level="note",
                    message=match.group("message"),
                    error_code=None,
                )
            else:
                return None
        else:
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
        pattern = self.config.custom_summary_pattern or SUMMARY_PATTERN
        match = pattern.match(line.strip())
        if not match:
            return False

        # For custom patterns, assume group 3 contains files checked
        # or the last numeric group if there are fewer groups
        if self.config.custom_summary_pattern:
            # Find the last numeric group (for flexibility)
            numeric_groups = [g for g in match.groups() if g and g.isdigit()]
            if numeric_groups:
                self.files_checked = int(numeric_groups[-1])
        else:
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
                if self.config.debug:
                    print(f"[DEBUG] Line {line_number}: Parsed as diagnostic")
                self.diagnostics.append(diagnostic)
                self.current_diagnostic = diagnostic
                parsed = True
            elif note := self._try_parse_note(line):
                # Try to associate with current diagnostic, otherwise standalone
                if self.config.debug:
                    print(f"[DEBUG] Line {line_number}: Parsed as note")
                self._associate_note_with_diagnostic(note.message)
                if self.current_diagnostic is None:
                    self.standalone_notes.append(note)
                parsed = True
            elif self._try_parse_summary(line):
                if self.config.debug:
                    print(f"[DEBUG] Line {line_number}: Parsed as summary")
                parsed = True

            # If line wasn't parsed by any pattern, track as parse error
            if not parsed:
                if self.config.debug:
                    print(f"[DEBUG] Line {line_number}: No pattern matched - '{line}'")
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
