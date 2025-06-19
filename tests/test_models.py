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
