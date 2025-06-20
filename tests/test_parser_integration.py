"""Integration tests for mypy output parser with real output samples."""

import pytest

from dr_cli.typecheck.parser import MypyOutputParser
from tests.fixtures.mypy_output_samples import (
    SIMPLE_ERROR_OUTPUT,
    MULTIPLE_ERRORS_OUTPUT,
    MULTI_FILE_OUTPUT,
    EMPTY_OUTPUT,
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