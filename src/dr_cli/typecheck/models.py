"""Pydantic models for mypy output parsing."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator, computed_field


class MessageLevel(str, Enum):
    """Mypy message severity levels."""

    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"


class Location(BaseModel):
    """Represents a location in source code."""

    file: str
    line: int
    column: int | None = None
    end_line: int | None = None
    end_column: int | None = None


class MypyMessage(BaseModel):
    """Base class for all mypy messages."""

    location: Location
    level: MessageLevel
    message: str


class MypyDiagnostic(MypyMessage):
    """Error or warning with an error code and optional associated notes."""

    error_code: str
    notes: list[str] = Field(default_factory=list)

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: MessageLevel) -> MessageLevel:
        """Validate that diagnostic level is error or warning, not note."""
        if v == MessageLevel.NOTE:
            raise ValueError("Notes cannot be MypyDiagnostic instances")
        return v

    def to_jsonl_dict(self) -> dict[str, str | int | None]:
        """Convert diagnostic to flat dict for JSONL output (excludes notes)."""
        return {
            "file": self.location.file,
            "line": self.location.line,
            "column": self.location.column,
            "level": self.level.value,
            "message": self.message,
            "error_code": self.error_code,
        }


class MypyNote(MypyMessage):
    """Standalone note (reveal_type, context headers, etc.)."""

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: MessageLevel) -> MessageLevel:
        """Validate that note level is NOTE."""
        if v != MessageLevel.NOTE:
            raise ValueError("MypyNote must have NOTE level")
        return v


class ParseError(BaseModel):
    """Represents a line that could not be parsed."""

    line_number: int
    line_content: str
    reason: str | None = None


class MypyResults(BaseModel):
    """Aggregated results from type checking."""

    diagnostics: list[MypyDiagnostic]
    standalone_notes: list[MypyNote]
    files_checked: int
    parse_errors: list[ParseError] = Field(default_factory=list)

    @computed_field
    @property
    def errors(self) -> list[MypyDiagnostic]:
        """Get all error diagnostics."""
        return [d for d in self.diagnostics if d.level == MessageLevel.ERROR]

    @computed_field
    @property
    def warnings(self) -> list[MypyDiagnostic]:
        """Get all warning diagnostics."""
        return [d for d in self.diagnostics if d.level == MessageLevel.WARNING]

    @computed_field
    @property
    def error_count(self) -> int:
        """Count of error diagnostics."""
        return len(self.errors)

    @computed_field
    @property
    def warning_count(self) -> int:
        """Count of warning diagnostics."""
        return len(self.warnings)

    @computed_field
    @property
    def files_with_errors(self) -> set[str]:
        """Set of files containing errors."""
        return {d.location.file for d in self.errors}

    def format_summary(self) -> str:
        """Format mypy-style summary line."""
        num_files = len(self.files_with_errors)
        error_word = "error" if self.error_count == 1 else "errors"
        file_word = "file" if num_files == 1 else "files"
        source_word = "file" if self.files_checked == 1 else "files"
        return (
            f"Found {self.error_count} {error_word} in {num_files} {file_word} "
            f"(checked {self.files_checked} source {source_word})"
        )

    def write_errors_as_jsonl(self, output_path: str) -> None:
        """Write error diagnostics to a JSONL file."""
        import json
        from pathlib import Path

        path = Path(output_path)
        with path.open("w") as f:
            for error in self.errors:
                json_line = json.dumps(error.to_jsonl_dict())
                f.write(json_line + "\n")

    @classmethod
    def merge(cls, results: list["MypyResults"]) -> "MypyResults":
        """Merge multiple MypyResults into a single combined result."""
        if not results:
            return cls(diagnostics=[], standalone_notes=[], files_checked=0)

        if len(results) == 1:
            return results[0]

        # Combine all diagnostics, notes, and errors
        all_diagnostics = []
        all_notes = []
        all_parse_errors = []
        total_files = 0

        for result in results:
            all_diagnostics.extend(result.diagnostics)
            all_notes.extend(result.standalone_notes)
            all_parse_errors.extend(result.parse_errors)
            total_files += result.files_checked

        return cls(
            diagnostics=all_diagnostics,
            standalone_notes=all_notes,
            files_checked=total_files,
            parse_errors=all_parse_errors,
        )
