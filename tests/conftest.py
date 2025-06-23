"""Shared test fixtures for dr_cli typecheck tests."""

import pytest

from dr_cli.typecheck.models import (
    MypyDiagnostic,
    MypyResults,
    Location,
    MessageLevel,
)


@pytest.fixture
def sample_error_diagnostic() -> MypyDiagnostic:
    """Create a sample error diagnostic for testing."""
    return MypyDiagnostic(
        location=Location(file="test.py", line=1, column=5),
        level=MessageLevel.ERROR,
        message="Incompatible types in assignment",
        error_code="assignment",
        notes=["Variable is declared as 'int'"],
    )


@pytest.fixture
def sample_warning_diagnostic() -> MypyDiagnostic:
    """Create a sample warning diagnostic for testing."""
    return MypyDiagnostic(
        location=Location(file="test.py", line=2),
        level=MessageLevel.WARNING,
        message="Unused variable 'x'",
        error_code="unused-variable",
    )


@pytest.fixture
def multi_file_results(
    sample_error_diagnostic: MypyDiagnostic, sample_warning_diagnostic: MypyDiagnostic
) -> MypyResults:
    """Create sample results with multiple files and diagnostics."""
    error_in_other_file = MypyDiagnostic(
        location=Location(file="other.py", line=10, column=2),
        level=MessageLevel.ERROR,
        message="Name 'undefined_var' is not defined",
        error_code="name-defined",
    )

    return MypyResults(
        diagnostics=[
            sample_error_diagnostic,
            sample_warning_diagnostic,
            error_in_other_file,
        ],
        standalone_notes=[],
        files_checked=2,
    )
