import pytest
from pydantic import ValidationError
from dr_cli.typecheck.models import (
    MessageLevel,
    Location,
    MypyMessage,
    MypyDiagnostic,
    MypyNote,
    MypyResults,
)


@pytest.fixture
def sample_location():
    return Location(file="test.py", line=10, column=5)


@pytest.fixture
def sample_error():
    return MypyDiagnostic(
        location=Location(file="test.py", line=10),
        level=MessageLevel.ERROR,
        message="Test error",
        error_code="test-error",
    )


@pytest.fixture
def sample_warning():
    return MypyDiagnostic(
        location=Location(file="test.py", line=20),
        level=MessageLevel.WARNING,
        message="Test warning",
        error_code="test-warning",
    )


def test_diagnostic_accepts_error_level(sample_location):
    """Test that MypyDiagnostic accepts ERROR level."""
    diagnostic = MypyDiagnostic(
        location=sample_location,
        level=MessageLevel.ERROR,
        message="Test error",
        error_code="test-error"
    )
    assert diagnostic.level == MessageLevel.ERROR


def test_diagnostic_accepts_warning_level(sample_location):
    """Test that MypyDiagnostic accepts WARNING level."""
    diagnostic = MypyDiagnostic(
        location=sample_location,
        level=MessageLevel.WARNING,
        message="Test warning",
        error_code="test-warning"
    )
    assert diagnostic.level == MessageLevel.WARNING


def test_diagnostic_rejects_note_level(sample_location):
    """Test that MypyDiagnostic rejects NOTE level with proper error."""
    with pytest.raises(ValidationError) as exc_info:
        MypyDiagnostic(
            location=sample_location,
            level=MessageLevel.NOTE,
            message="Test note",
            error_code="test-note"
        )
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('level',)
    assert "Notes cannot be MypyDiagnostic instances" in errors[0]['msg']


def test_note_accepts_note_level(sample_location):
    """Test that MypyNote accepts NOTE level."""
    note = MypyNote(
        location=sample_location,
        level=MessageLevel.NOTE,
        message="Test note"
    )
    assert note.level == MessageLevel.NOTE


@pytest.mark.parametrize("level", [MessageLevel.ERROR, MessageLevel.WARNING])
def test_note_rejects_non_note_levels(sample_location, level):
    """Test that MypyNote rejects ERROR/WARNING levels."""
    with pytest.raises(ValidationError) as exc_info:
        MypyNote(
            location=sample_location,
            level=level,
            message="Test message"
        )
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('level',)
    assert "MypyNote must have NOTE level" in errors[0]['msg']


@pytest.fixture
def sample_results():
    """Create MypyResults with mixed diagnostics."""
    error1 = MypyDiagnostic(
        location=Location(file="file1.py", line=10),
        level=MessageLevel.ERROR,
        message="First error",
        error_code="error-1"
    )
    error2 = MypyDiagnostic(
        location=Location(file="file2.py", line=20),
        level=MessageLevel.ERROR,
        message="Second error",
        error_code="error-2"
    )
    warning = MypyDiagnostic(
        location=Location(file="file1.py", line=30),
        level=MessageLevel.WARNING,
        message="First warning",
        error_code="warning-1"
    )
    
    return MypyResults(
        diagnostics=[error1, warning, error2],
        standalone_notes=[],
        files_checked=3
    )


def test_results_errors_property_filters_only_errors(sample_results):
    """Test that errors property returns only ERROR diagnostics."""
    errors = sample_results.errors
    
    assert len(errors) == 2
    assert all(diag.level == MessageLevel.ERROR for diag in errors)
    assert errors[0].message == "First error"
    assert errors[1].message == "Second error"


def test_results_warnings_property_filters_only_warnings(sample_results):
    """Test that warnings property returns only WARNING diagnostics."""
    warnings = sample_results.warnings
    
    assert len(warnings) == 1
    assert warnings[0].level == MessageLevel.WARNING
    assert warnings[0].message == "First warning"


def test_results_error_count_returns_correct_count(sample_results):
    """Test that error_count returns the correct number of errors."""
    assert sample_results.error_count == 2


def test_results_warning_count_returns_correct_count(sample_results):
    """Test that warning_count returns the correct number of warnings."""
    assert sample_results.warning_count == 1


def test_results_counts_with_empty_diagnostics():
    """Test count properties with no diagnostics."""
    empty_results = MypyResults(
        diagnostics=[],
        standalone_notes=[],
        files_checked=0
    )
    
    assert empty_results.error_count == 0
    assert empty_results.warning_count == 0


def test_results_files_with_errors_deduplicates_files(sample_results):
    """Test that files_with_errors deduplicates file names."""
    # sample_results has errors in file1.py and file2.py
    files_with_errors = sample_results.files_with_errors
    
    assert len(files_with_errors) == 2
    assert "file1.py" in files_with_errors
    assert "file2.py" in files_with_errors


def test_results_files_with_errors_excludes_warnings_only():
    """Test that files with only warnings don't appear in files_with_errors."""
    warning_only = MypyDiagnostic(
        location=Location(file="warning_file.py", line=10),
        level=MessageLevel.WARNING,
        message="Only warning",
        error_code="warning-only"
    )
    
    results = MypyResults(
        diagnostics=[warning_only],
        standalone_notes=[],
        files_checked=1
    )
    
    assert len(results.files_with_errors) == 0


def test_results_files_with_errors_empty_case():
    """Test files_with_errors with no diagnostics."""
    empty_results = MypyResults(
        diagnostics=[],
        standalone_notes=[],
        files_checked=0
    )
    
    assert len(empty_results.files_with_errors) == 0


@pytest.mark.parametrize("error_count,warning_count,file_count,files_checked,expected", [
    (0, 0, 0, 5, "Found 0 errors in 0 files (checked 5 source files)"),
    (1, 0, 1, 10, "Found 1 error in 1 file (checked 10 source files)"),
    (2, 1, 2, 15, "Found 2 errors in 2 files (checked 15 source files)"),
    (5, 3, 3, 20, "Found 5 errors in 3 files (checked 20 source files)"),
])
def test_format_summary_with_different_counts(error_count, warning_count, file_count, files_checked, expected):
    """Test format_summary with various error/warning/file counts."""
    # Create diagnostics to match the expected counts
    diagnostics = []
    files = [f"file{i}.py" for i in range(file_count)]
    
    # Add errors distributed across files
    for i in range(error_count):
        file_index = i % len(files) if files else 0
        file_name = files[file_index] if files else "test.py"
        diagnostics.append(MypyDiagnostic(
            location=Location(file=file_name, line=10 + i),
            level=MessageLevel.ERROR,
            message=f"Error {i+1}",
            error_code=f"error-{i+1}"
        ))
    
    # Add warnings
    for i in range(warning_count):
        file_index = i % len(files) if files else 0
        file_name = files[file_index] if files else "test.py"
        diagnostics.append(MypyDiagnostic(
            location=Location(file=file_name, line=50 + i),
            level=MessageLevel.WARNING,
            message=f"Warning {i+1}",
            error_code=f"warning-{i+1}"
        ))
    
    results = MypyResults(
        diagnostics=diagnostics,
        standalone_notes=[],
        files_checked=files_checked
    )
    
    assert results.format_summary() == expected
