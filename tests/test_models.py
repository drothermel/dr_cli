"""Tests for mypy output parser Pydantic models."""

import pytest
from pydantic import ValidationError
from dr_cli.typecheck.models import (
    MessageLevel,
    Location,
    MypyDiagnostic,
    MypyNote,
    MypyResults,
    ParseError,
)


@pytest.fixture
def sample_location() -> Location:
    """Create a sample Location for testing."""
    return Location(file="test.py", line=10, column=5)


@pytest.fixture
def sample_error() -> MypyDiagnostic:
    """Create a sample MypyDiagnostic with error level."""
    return MypyDiagnostic(
        location=Location(file="test.py", line=10),
        level=MessageLevel.ERROR,
        message="Test error",
        error_code="test-error",
    )


@pytest.fixture
def sample_warning() -> MypyDiagnostic:
    """Create a sample MypyDiagnostic with warning level."""
    return MypyDiagnostic(
        location=Location(file="test.py", line=20),
        level=MessageLevel.WARNING,
        message="Test warning",
        error_code="test-warning",
    )


def test_diagnostic_accepts_error_level(sample_location: Location) -> None:
    """Test that MypyDiagnostic accepts ERROR level."""
    diagnostic = MypyDiagnostic(
        location=sample_location,
        level=MessageLevel.ERROR,
        message="Test error",
        error_code="test-error",
    )
    assert diagnostic.level == MessageLevel.ERROR


def test_diagnostic_accepts_warning_level(sample_location: Location) -> None:
    """Test that MypyDiagnostic accepts WARNING level."""
    diagnostic = MypyDiagnostic(
        location=sample_location,
        level=MessageLevel.WARNING,
        message="Test warning",
        error_code="test-warning",
    )
    assert diagnostic.level == MessageLevel.WARNING


def test_diagnostic_rejects_note_level(sample_location: Location) -> None:
    """Test that MypyDiagnostic rejects NOTE level with proper error."""
    with pytest.raises(ValidationError) as exc_info:
        MypyDiagnostic(
            location=sample_location,
            level=MessageLevel.NOTE,
            message="Test note",
            error_code="test-note",
        )

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("level",)
    assert "Notes cannot be MypyDiagnostic instances" in errors[0]["msg"]


def test_note_accepts_note_level(sample_location: Location) -> None:
    """Test that MypyNote accepts NOTE level."""
    note = MypyNote(
        location=sample_location, level=MessageLevel.NOTE, message="Test note"
    )
    assert note.level == MessageLevel.NOTE


@pytest.mark.parametrize("level", [MessageLevel.ERROR, MessageLevel.WARNING])
def test_note_rejects_non_note_levels(
    sample_location: Location, level: MessageLevel
) -> None:
    """Test that MypyNote rejects ERROR/WARNING levels."""
    with pytest.raises(ValidationError) as exc_info:
        MypyNote(location=sample_location, level=level, message="Test message")

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("level",)
    assert "MypyNote must have NOTE level" in errors[0]["msg"]


@pytest.fixture
def sample_results() -> MypyResults:
    """Create MypyResults with mixed diagnostics."""
    error1 = MypyDiagnostic(
        location=Location(file="file1.py", line=10),
        level=MessageLevel.ERROR,
        message="First error",
        error_code="error-1",
    )
    error2 = MypyDiagnostic(
        location=Location(file="file2.py", line=20),
        level=MessageLevel.ERROR,
        message="Second error",
        error_code="error-2",
    )
    warning = MypyDiagnostic(
        location=Location(file="file1.py", line=30),
        level=MessageLevel.WARNING,
        message="First warning",
        error_code="warning-1",
    )

    return MypyResults(
        diagnostics=[error1, warning, error2], standalone_notes=[], files_checked=3
    )


def test_results_errors_property_filters_only_errors(
    sample_results: MypyResults,
) -> None:
    """Test that errors property returns only ERROR diagnostics."""
    errors = sample_results.errors

    assert len(errors) == 2
    assert all(diag.level == MessageLevel.ERROR for diag in errors)
    assert errors[0].message == "First error"
    assert errors[1].message == "Second error"


def test_results_warnings_property_filters_only_warnings(
    sample_results: MypyResults,
) -> None:
    """Test that warnings property returns only WARNING diagnostics."""
    warnings = sample_results.warnings

    assert len(warnings) == 1
    assert warnings[0].level == MessageLevel.WARNING
    assert warnings[0].message == "First warning"


def test_results_error_count_returns_correct_count(sample_results: MypyResults) -> None:
    """Test that error_count returns the correct number of errors."""
    assert sample_results.error_count == 2


def test_results_warning_count_returns_correct_count(
    sample_results: MypyResults,
) -> None:
    """Test that warning_count returns the correct number of warnings."""
    assert sample_results.warning_count == 1


def test_results_counts_with_empty_diagnostics() -> None:
    """Test count properties with no diagnostics."""
    empty_results = MypyResults(diagnostics=[], standalone_notes=[], files_checked=0)

    assert empty_results.error_count == 0
    assert empty_results.warning_count == 0


def test_results_files_with_errors_deduplicates_files(
    sample_results: MypyResults,
) -> None:
    """Test that files_with_errors deduplicates file names."""
    # sample_results has errors in file1.py and file2.py
    files_with_errors = sample_results.files_with_errors

    assert len(files_with_errors) == 2
    assert "file1.py" in files_with_errors
    assert "file2.py" in files_with_errors


def test_results_files_with_errors_excludes_warnings_only() -> None:
    """Test that files with only warnings don't appear in files_with_errors."""
    warning_only = MypyDiagnostic(
        location=Location(file="warning_file.py", line=10),
        level=MessageLevel.WARNING,
        message="Only warning",
        error_code="warning-only",
    )

    results = MypyResults(
        diagnostics=[warning_only], standalone_notes=[], files_checked=1
    )

    assert len(results.files_with_errors) == 0


def test_results_files_with_errors_empty_case() -> None:
    """Test files_with_errors with no diagnostics."""
    empty_results = MypyResults(diagnostics=[], standalone_notes=[], files_checked=0)

    assert len(empty_results.files_with_errors) == 0


@pytest.mark.parametrize(
    ("error_count", "warning_count", "file_count", "files_checked", "expected"),
    [
        (0, 0, 0, 5, "Found 0 errors in 0 files (checked 5 source files)"),
        (1, 0, 1, 10, "Found 1 error in 1 file (checked 10 source files)"),
        (2, 1, 2, 15, "Found 2 errors in 2 files (checked 15 source files)"),
        (5, 3, 3, 20, "Found 5 errors in 3 files (checked 20 source files)"),
    ],
)
def test_format_summary_with_different_counts(
    error_count: int,
    warning_count: int,
    file_count: int,
    files_checked: int,
    expected: str,
) -> None:
    """Test format_summary with various error/warning/file counts."""
    # Create diagnostics to match the expected counts
    diagnostics = []
    files = [f"file{i}.py" for i in range(file_count)]

    # Add errors distributed across files
    for i in range(error_count):
        file_index = i % len(files) if files else 0
        file_name = files[file_index] if files else "test.py"
        diagnostics.append(
            MypyDiagnostic(
                location=Location(file=file_name, line=10 + i),
                level=MessageLevel.ERROR,
                message=f"Error {i + 1}",
                error_code=f"error-{i + 1}",
            )
        )

    # Add warnings
    for i in range(warning_count):
        file_index = i % len(files) if files else 0
        file_name = files[file_index] if files else "test.py"
        diagnostics.append(
            MypyDiagnostic(
                location=Location(file=file_name, line=50 + i),
                level=MessageLevel.WARNING,
                message=f"Warning {i + 1}",
                error_code=f"warning-{i + 1}",
            )
        )

    results = MypyResults(
        diagnostics=diagnostics, standalone_notes=[], files_checked=files_checked
    )

    assert results.format_summary() == expected


def test_diagnostic_notes_initialization() -> None:
    """Test that diagnostic notes list is initialized correctly."""
    diagnostic = MypyDiagnostic(
        location=Location(file="test.py", line=10),
        level=MessageLevel.ERROR,
        message="Test error",
        error_code="test-error",
    )

    assert diagnostic.notes == []


def test_diagnostic_with_notes() -> None:
    """Test diagnostic with notes added."""
    diagnostic = MypyDiagnostic(
        location=Location(file="test.py", line=10),
        level=MessageLevel.ERROR,
        message="Test error",
        error_code="test-error",
        notes=["This is a helpful note", "Another note for context"],
    )

    assert len(diagnostic.notes) == 2
    assert "This is a helpful note" in diagnostic.notes
    assert "Another note for context" in diagnostic.notes


def test_diagnostic_notes_can_be_added() -> None:
    """Test that notes can be added to diagnostic after creation."""
    diagnostic = MypyDiagnostic(
        location=Location(file="test.py", line=10),
        level=MessageLevel.ERROR,
        message="Test error",
        error_code="test-error",
    )

    diagnostic.notes.append("Added note")
    assert len(diagnostic.notes) == 1
    assert diagnostic.notes[0] == "Added note"


def test_location_with_only_required_fields() -> None:
    """Test Location with only file and line (no column/end)."""
    location = Location(file="test.py", line=42)

    assert location.file == "test.py"
    assert location.line == 42
    assert location.column is None
    assert location.end_line is None
    assert location.end_column is None


def test_location_with_column() -> None:
    """Test Location with file, line, and column."""
    location = Location(file="test.py", line=42, column=13)

    assert location.file == "test.py"
    assert location.line == 42
    assert location.column == 13
    assert location.end_line is None
    assert location.end_column is None


def test_location_with_end_position() -> None:
    """Test Location with end line and column."""
    location = Location(file="test.py", line=42, column=13, end_line=43, end_column=20)

    assert location.file == "test.py"
    assert location.line == 42
    assert location.column == 13
    assert location.end_line == 43
    assert location.end_column == 20


def test_results_model_dump_includes_computed_properties(
    sample_results: MypyResults,
) -> None:
    """Test that model_dump includes computed properties."""
    data = sample_results.model_dump()

    # Verify computed properties are included
    assert "error_count" in data
    assert "warning_count" in data
    assert "files_with_errors" in data
    assert data["error_count"] == 2
    assert data["warning_count"] == 1
    assert len(data["files_with_errors"]) == 2


def test_results_json_serialization_includes_computed_fields(
    sample_results: MypyResults,
) -> None:
    """Test that JSON serialization includes computed fields."""
    json_str = sample_results.model_dump_json()

    # Verify computed fields appear in JSON
    assert '"error_count":2' in json_str
    assert '"warning_count":1' in json_str
    assert '"files_with_errors":[' in json_str


def test_diagnostic_serialization() -> None:
    """Test that MypyDiagnostic serializes correctly."""
    diagnostic = MypyDiagnostic(
        location=Location(file="test.py", line=10, column=5),
        level=MessageLevel.ERROR,
        message="Test error",
        error_code="test-error",
        notes=["Test note"],
    )

    data = diagnostic.model_dump()

    # Verify all fields are present
    assert data["location"]["file"] == "test.py"
    assert data["location"]["line"] == 10
    assert data["location"]["column"] == 5
    assert data["level"] == "error"
    assert data["message"] == "Test error"
    assert data["error_code"] == "test-error"
    assert data["notes"] == ["Test note"]


def test_diagnostic_to_jsonl_dict() -> None:
    """Test MypyDiagnostic to_jsonl_dict method for JSONL serialization."""
    diagnostic = MypyDiagnostic(
        location=Location(file="test.py", line=10, column=5),
        level=MessageLevel.ERROR,
        message="Test error message",
        error_code="test-error",
        notes=["Test note 1", "Test note 2"],
    )

    result = diagnostic.to_jsonl_dict()

    # Should include basic fields but not notes
    assert result == {
        "file": "test.py",
        "line": 10,
        "column": 5,
        "level": "error",
        "message": "Test error message",
        "error_code": "test-error",
    }


def test_diagnostic_to_jsonl_dict_without_column() -> None:
    """Test to_jsonl_dict when diagnostic has no column number."""
    diagnostic = MypyDiagnostic(
        location=Location(file="module.py", line=42),
        level=MessageLevel.WARNING,
        message="Warning message",
        error_code="warn-code",
    )

    result = diagnostic.to_jsonl_dict()

    assert result == {
        "file": "module.py",
        "line": 42,
        "column": None,
        "level": "warning",
        "message": "Warning message",
        "error_code": "warn-code",
    }


def test_parse_error_creation() -> None:
    """Test ParseError model creation."""
    error = ParseError(
        line_number=10,
        line_content="Invalid line that couldn't be parsed",
        reason="No pattern matched",
    )

    assert error.line_number == 10
    assert error.line_content == "Invalid line that couldn't be parsed"
    assert error.reason == "No pattern matched"


def test_parse_error_optional_reason() -> None:
    """Test ParseError with optional reason field."""
    error = ParseError(
        line_number=5,
        line_content="Some unparseable content",
    )

    assert error.line_number == 5
    assert error.line_content == "Some unparseable content"
    assert error.reason is None


def test_results_with_parse_errors() -> None:
    """Test MypyResults can include parse errors."""
    results = MypyResults(
        diagnostics=[],
        standalone_notes=[],
        files_checked=1,
        parse_errors=[
            ParseError(line_number=1, line_content="Bad line 1"),
            ParseError(
                line_number=3, line_content="Bad line 3", reason="Unknown format"
            ),
        ],
    )

    assert len(results.parse_errors) == 2
    assert results.parse_errors[0].line_number == 1
    assert results.parse_errors[1].reason == "Unknown format"
