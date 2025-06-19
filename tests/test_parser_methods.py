"""Tests for mypy output parser methods."""

import pytest

from dr_cli.typecheck.models import MessageLevel, MypyDiagnostic, MypyNote
from dr_cli.typecheck.parser import MypyOutputParser


@pytest.fixture
def parser() -> MypyOutputParser:
    """Create a fresh parser instance."""
    return MypyOutputParser()


class TestParserMethods:
    """Test parser methods that create models from parsed data."""
    
    def test_diagnostic_parsing_creates_error_model(self, parser: MypyOutputParser) -> None:
        """Test parsing error line creates correct MypyDiagnostic model."""
        line = "file.py:10: error: Message text [error-code]"
        diagnostic = parser._try_parse_diagnostic(line)
        
        assert diagnostic is not None
        assert diagnostic.location.file == "file.py"
        assert diagnostic.location.line == 10
        assert diagnostic.level == MessageLevel.ERROR
        assert diagnostic.message == "Message text"
        assert diagnostic.error_code == "error-code"
    
    def test_diagnostic_parsing_creates_warning_model(self, parser: MypyOutputParser) -> None:
        """Test parsing warning line creates correct MypyDiagnostic model."""
        line = "file.py:10:5: warning: Message text [warn-code]"
        diagnostic = parser._try_parse_diagnostic(line)
        
        assert diagnostic is not None
        assert diagnostic.location.column == 5
        assert diagnostic.level == MessageLevel.WARNING
        assert diagnostic.error_code == "warn-code"
    
    def test_note_parsing_creates_model(self, parser: MypyOutputParser) -> None:
        """Test parsing note line creates correct MypyNote model."""
        line = "file.py:10: note: This is a note"
        note = parser._try_parse_note(line)
        
        assert note is not None
        assert note.location.file == "file.py"
        assert note.location.line == 10
        assert note.location.column is None
        assert note.level == MessageLevel.NOTE
        assert note.message == "This is a note"
    
    def test_note_parsing_with_column(self, parser: MypyOutputParser) -> None:
        """Test parsing note with column creates correct model."""
        line = "file.py:10:5: note: Note with column"
        note = parser._try_parse_note(line)
        
        assert note is not None
        assert note.location.column == 5
    
    def test_note_association_with_diagnostic(self, parser: MypyOutputParser) -> None:
        """Test notes are associated with current diagnostic."""
        # Parse a diagnostic first
        error_line = "file.py:10: error: Message [code]"
        diagnostic = parser._try_parse_diagnostic(error_line)
        parser.diagnostics.append(diagnostic)
        parser.current_diagnostic = diagnostic
        
        # Associate a note with it
        parser._associate_note_with_diagnostic("This is a note message")
        
        assert len(diagnostic.notes) == 1
        assert diagnostic.notes[0] == "This is a note message"
    
    def test_note_association_without_diagnostic(self, parser: MypyOutputParser) -> None:
        """Test notes without current diagnostic are handled gracefully."""
        # No current diagnostic
        parser.current_diagnostic = None
        
        # Try to associate note
        parser._associate_note_with_diagnostic("Standalone note")
        
        # Should not crash, note is just ignored for association
        assert len(parser.diagnostics) == 0
    
    def test_summary_parsing_updates_state(self, parser: MypyOutputParser) -> None:
        """Test summary line updates files_checked state."""
        line = "Found 1 error in 1 file (checked 5 source files)"
        result = parser._try_parse_summary(line)
        
        assert result is True
        assert parser.files_checked == 5
    
    def test_summary_parsing_plural_files(self, parser: MypyOutputParser) -> None:
        """Test summary with plural files updates state correctly."""
        line = "Found 3 errors in 2 files (checked 10 source files)"
        result = parser._try_parse_summary(line)
        
        assert result is True
        assert parser.files_checked == 10