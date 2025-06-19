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