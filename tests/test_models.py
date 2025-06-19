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
