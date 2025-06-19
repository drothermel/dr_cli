"""Pydantic models for mypy output parsing."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator


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

    @field_validator('level')
    @classmethod
    def validate_level(cls, v: MessageLevel) -> MessageLevel:
        """Validate that diagnostic level is error or warning, not note."""
        if v == MessageLevel.NOTE:
            raise ValueError("Notes cannot be MypyDiagnostic instances")
        return v


class MypyNote(MypyMessage):
    """Standalone note (reveal_type, context headers, etc.)"""

    @field_validator('level')
    @classmethod
    def validate_level(cls, v: MessageLevel) -> MessageLevel:
        """Validate that note level is NOTE."""
        if v != MessageLevel.NOTE:
            raise ValueError("MypyNote must have NOTE level")
        return v
