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


class MypyNote(MypyMessage):
    """Standalone note (reveal_type, context headers, etc.)"""

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: MessageLevel) -> MessageLevel:
        """Validate that note level is NOTE."""
        if v != MessageLevel.NOTE:
            raise ValueError("MypyNote must have NOTE level")
        return v


class MypyResults(BaseModel):
    """Aggregated results from type checking."""

    diagnostics: list[MypyDiagnostic]
    standalone_notes: list[MypyNote]
    files_checked: int

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
