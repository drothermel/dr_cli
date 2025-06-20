"""Integration tests for mypy output parser with real output samples."""

import pytest

from dr_cli.typecheck.parser import MypyOutputParser
from tests.fixtures.mypy_output_samples import (
    SIMPLE_ERROR_OUTPUT,
    MULTIPLE_ERRORS_OUTPUT,
    MULTI_FILE_OUTPUT,
    EMPTY_OUTPUT,
    ERROR_WITH_NOTES_OVERLOAD,
)


class TestParserIntegration:
    """Test full parsing workflow with real mypy output."""
    
    @pytest.fixture
    def parser(self) -> MypyOutputParser:
        """Create a fresh parser instance."""
        return MypyOutputParser()
    
    def test_parse_simple_single_error(self, parser: MypyOutputParser) -> None:
        """Test parsing basic single error output."""
        results = parser.parse_output(SIMPLE_ERROR_OUTPUT)
        
        assert len(results.diagnostics) == 1
        assert results.error_count == 1
        assert results.warning_count == 0
        assert results.files_checked == 1
        
        error = results.diagnostics[0]
        assert error.location.file == "tests/fixtures/sample_code/simple_error.py"
        assert error.location.line == 10
        assert error.error_code == "arg-type"
    
    def test_parse_error_with_associated_notes(self, parser: MypyOutputParser) -> None:
        """Test parsing error with notes attached."""
        results = parser.parse_output(ERROR_WITH_NOTES_OVERLOAD)
        
        assert len(results.diagnostics) == 2
        assert results.files_checked == 1
        
        # Second error should have notes attached
        overload_error = results.diagnostics[1]
        assert overload_error.error_code == "call-overload"
        assert len(overload_error.notes) == 3
        assert "Possible overload variants:" in overload_error.notes[0]
        assert "def process(x: int) -> str" in overload_error.notes[1]
        assert "def process(x: str) -> int" in overload_error.notes[2]