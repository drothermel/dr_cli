"""Pydantic models for mypy output parsing."""

from enum import Enum
from pydantic import BaseModel


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
