# Pydantic Models Testing Implementation Plan

## Context and Background

### What We're Building
We're creating an extensible mypy output parser using Pydantic models. The models are already implemented in `src/dr_cli/typecheck/models.py`:
- `MessageLevel` enum (ERROR, WARNING, NOTE)
- `Location` model for file positions
- `MypyMessage` base class
- `MypyDiagnostic` for errors/warnings with validation
- `MypyNote` for standalone notes with validation
- `MypyResults` for aggregated results with computed properties

### Working Principles
1. **Small, focused commits**: Each commit adds one specific piece of functionality (~20-30 lines)
2. **Semantic commit messages**: Clear, concise messages that describe the change
3. **Test what matters**: Focus on custom logic, not Pydantic's built-in functionality
4. **Use shortcuts**: Git aliases from CLAUDE.md (gst, gd_agent, ga, gc, glo)
5. **Fix only our lints**: Run `lint_fix` before commits, fix only issues in our code

### Testing Philosophy
**Test:**
- Custom validators (our `validate_level` methods)
- Computed properties (@property methods in MypyResults)
- Edge cases and error scenarios
- Integration between models

**Don't Test:**
- Basic Pydantic validation (type checking, required fields)
- Simple getters/setters
- Pydantic's serialization (it's already tested)

## Implementation Plan

### Phase 1: Test Infrastructure Setup

#### Commit 1: "Add test structure and fixtures"
```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from dr_cli.typecheck.models import (
    MessageLevel, Location, MypyMessage, 
    MypyDiagnostic, MypyNote, MypyResults
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
        error_code="test-error"
    )

@pytest.fixture
def sample_warning():
    return MypyDiagnostic(
        location=Location(file="test.py", line=20),
        level=MessageLevel.WARNING,
        message="Test warning",
        error_code="test-warning"
    )
```

### Phase 2: Validator Testing

#### Commit 2: "Test MypyDiagnostic level validator"
- Test accepts ERROR level
- Test accepts WARNING level  
- Test rejects NOTE level with proper error

#### Commit 3: "Test MypyNote level validator"
- Test accepts NOTE level
- Test rejects ERROR/WARNING with parametrized test

### Phase 3: Computed Properties Testing

#### Commit 4: "Test MypyResults error filtering"
- Test `errors` property filters only ERROR diagnostics
- Test `warnings` property filters only WARNING diagnostics

#### Commit 5: "Test MypyResults count properties"
- Test `error_count` returns correct count
- Test `warning_count` returns correct count

#### Commit 6: "Test files_with_errors property"
- Test deduplication of files
- Test empty case
- Test warnings don't appear in files_with_errors

#### Commit 7: "Test format_summary method"
- Parametrized test for different counts
- Test singular/plural handling

### Phase 4: Integration Testing

#### Commit 8: "Test diagnostic with notes integration"
- Test notes list initialization
- Test adding notes to diagnostic

#### Commit 9: "Test Location optional fields"
- Test with/without column numbers
- Test with/without end positions

#### Commit 10: "Test model serialization includes computed fields"
- Test model_dump includes computed properties
- Test JSON serialization

## Current Status
- ✅ Models implemented
- ✅ Documentation updated
- ⏳ Tests not started

## Commands Reference
```bash
# Check status
gst

# Create test file
touch tests/test_models.py

# After each commit:
lint_fix                    # Fix formatting
gst                        # Check status
gd_agent                   # Review changes
ga tests/test_models.py    # Stage test file
gc -m "commit message"     # Commit

# View progress
glo                        # See commit history
```

## Key Testing Patterns

### Validation Error Testing
```python
with pytest.raises(ValidationError) as exc_info:
    MypyDiagnostic(level=MessageLevel.NOTE, ...)
    
errors = exc_info.value.errors()
assert errors[0]['loc'] == ('level',)
assert "Notes cannot be MypyDiagnostic" in errors[0]['msg']
```

### Parametrized Testing
```python
@pytest.mark.parametrize("level", [MessageLevel.ERROR, MessageLevel.WARNING])
def test_note_rejects_non_note_levels(sample_location, level):
    with pytest.raises(ValidationError):
        MypyNote(location=sample_location, level=level, message="test")
```

### Computed Property Testing
```python
def test_computed_property():
    results = MypyResults(diagnostics=[...], standalone_notes=[], files_checked=5)
    
    # Test property
    assert results.error_count == 2
    
    # Test in serialization
    data = results.model_dump()
    assert data['error_count'] == 2
```

## Next Steps After Memory Compaction
1. Create tests/test_models.py
2. Follow the commit plan above
3. Run pytest after each phase to verify
4. Once tests pass, move to parser implementation (see parser-implementation-plan.md)