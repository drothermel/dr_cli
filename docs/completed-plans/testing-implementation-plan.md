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

## Issues Found and Fixed During Implementation

### 1. Missing Pydantic Dependency
**Issue**: Tests failed with `ModuleNotFoundError: No module named 'pydantic'`
**Solution**: Added pydantic dependency with `uv add pydantic`
**Commit**: Included in "Test MypyDiagnostic level validator" commit

### 2. Computed Properties Not Serializing
**Issue**: `@property` methods didn't appear in `model_dump()` or JSON serialization
**Root Cause**: Pydantic v2 requires `@computed_field` decorator for properties to serialize
**Solution**: Added `@computed_field` decorator to all computed properties in MypyResults
**Fix**: 
```python
# Before (won't serialize)
@property
def error_count(self) -> int:
    return len(self.errors)

# After (will serialize)  
@computed_field
@property
def error_count(self) -> int:
    return len(self.errors)
```
**Commit**: "Test model serialization includes computed fields"

### 3. Format Summary Singular/Plural Issues
**Issue**: `format_summary()` always used plural forms ("errors", "files")
**Root Cause**: Method didn't handle singular cases (1 error, 1 file)
**Solution**: Added conditional logic for singular/plural word selection
**Fix**:
```python
error_word = "error" if self.error_count == 1 else "errors"
file_word = "file" if num_files == 1 else "files" 
source_word = "file" if self.files_checked == 1 else "files"
```
**Commit**: "Test format_summary method"

### 4. Validation Error Message Mismatch
**Issue**: Test expected "Notes must have NOTE level" but got "Value error, MypyNote must have NOTE level"
**Root Cause**: Pydantic prefixes custom validation errors with "Value error, "
**Solution**: Updated test assertions to use substring matching
**Fix**: `assert "MypyNote must have NOTE level" in errors[0]['msg']`
**Commit**: "Test MypyNote level validator"

## Implementation Retrospective & Learnings

### 🔍 **Critical Discoveries**

#### Pydantic v2 Serialization Behavior
- **Key Insight**: Regular `@property` methods are invisible to serialization
- **Impact**: Would have caused silent failures in real usage
- **Lesson**: Always test serialization when using computed properties

#### Error Message Precision
- **Pattern**: Framework error messages include prefixes/context  
- **Best Practice**: Use substring matching (`in`) rather than exact equality (`==`)
- **Future**: Inspect actual error outputs before writing assertions

### 🎯 **Effective Testing Strategies**

#### Dependency-Ordered Testing
**What worked**: Testing in logical dependency order:
1. Basic validation (field validators)
2. Computed properties (depend on basic fields)
3. Integration (models working together)  
4. Serialization (depends on everything)

**Why effective**: Failures point to root causes, not cascading effects

#### Fixture Composition Pattern
**Effective approach**: Building-block fixtures that compose:
```python
@pytest.fixture
def sample_location():
    return Location(file="test.py", line=10, column=5)

@pytest.fixture
def sample_error(sample_location):  # Reuses location
    return MypyDiagnostic(location=sample_location, ...)
```

**Benefits**: Reduces duplication, maintains consistency, easy to modify

#### Parametrized vs Individual Tests
- **Parametrized**: Excellent for systematic coverage of similar cases
- **Individual**: Better for unique behaviors needing specific context
- **Decision rule**: Use parametrized for data variations, individual for behavior variations

### 🚀 **Development Workflow Insights**

#### Small Commit Strategy
**Results**: 10 commits, ~20-30 lines each
**Benefits**:
- Easy to review with `gd_agent`
- Simple to revert if needed
- Clear purpose and scope
- Fast implementation cycles

**Key insight**: Granular commits forced better test organization

#### Documentation-Driven Development
**Approach**: Detailed planning document with specific examples
**Benefits**:
- No decision fatigue during implementation
- Consistent patterns across tests
- Easy resumption after interruptions
- Clear success criteria

**ROI**: Planning time investment paid off during implementation

### 📚 **Framework vs Custom Logic**

#### Testing Philosophy Validation
**What to test**: Custom validators, computed properties, business logic, edge cases
**What not to test**: Basic Pydantic validation, framework functionality

**Confirmed approach**: Trust the framework, test your additions

#### Modern Tooling Experience  
**Tools**: Pydantic + pytest + uv
**Experience**: Seamless when patterns are understood
**uv**: Dependency management was effortless (`uv add pydantic`)

### 🔧 **Technical Patterns**

#### Validation Error Testing Pattern
```python
with pytest.raises(ValidationError) as exc_info:
    Model(invalid_data)

errors = exc_info.value.errors()
assert len(errors) == 1
assert errors[0]['loc'] == ('field_name',)
assert "expected_message" in errors[0]['msg']
```

#### Computed Field Testing Pattern
```python
def test_computed_property():
    model = Model(data)
    
    # Test direct access
    assert model.computed_field == expected_value
    
    # Test serialization includes it
    data = model.model_dump()
    assert data['computed_field'] == expected_value
```

### 📋 **Future Reference Checklist**

For the next person implementing Pydantic model tests:

1. ✅ Plan test phases: validators → properties → integration → serialization
2. ✅ Use `@computed_field` for properties that should serialize
3. ✅ Test error messages with `in` not `==`  
4. ✅ Create composable fixtures
5. ✅ Use parametrized tests for systematic coverage
6. ✅ Focus on custom logic, not framework basics
7. ✅ Test serialization explicitly (`model_dump()`, `model_dump_json()`)
8. ✅ Keep commits small and semantically focused
9. ✅ Inspect actual outputs before writing assertions
10. ✅ Test in dependency order (simple → complex)

### 🎉 **Final Results**
- ✅ 27 test cases covering all custom logic
- ✅ 10 focused commits following the plan exactly
- ✅ Found and fixed 4 significant issues during testing
- ✅ Models ready for parser implementation phase

**Validation**: This thorough testing approach caught real issues that would have caused problems in production usage.

## Status: COMPLETED ✅
Implementation completed successfully. All 10 planned commits executed, all tests passing.

**Next Phase**: Move to parser implementation (see parser-implementation-plan.md)