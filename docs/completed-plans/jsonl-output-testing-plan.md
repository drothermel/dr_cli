# JSONL Output Testing Plan

## Overview
Comprehensive testing plan for JSONL output feature in dr_cli typecheck command.

## Testing Sequence

### Phase 1: Model Method Tests

**Test Commit 1: Add tests for MypyDiagnostic.to_jsonl_dict**
```
Add unit tests for MypyDiagnostic JSONL serialization
```
- Test basic error serialization
- Test with/without column numbers
- Test error codes handling
- ~20 lines in test_models.py

**Test Commit 2: Add tests for MypyResults.write_errors_as_jsonl**
```
Add unit tests for MypyResults JSONL file writing
```
- Test file creation and content
- Test filtering (errors only, no warnings/notes)
- Use tmp_path fixture
- ~22 lines in test_models.py

### Phase 2: Formatter Unit Tests

**Test Commit 3: Add base OutputFormatter tests**
```
Add tests for OutputFormatter abstract base class
```
- Test ABC enforcement
- Test subclass requirements
- ~15 lines in test_formatters.py

**Test Commit 4: Add TextFormatter output tests**
```
Add unit tests for TextFormatter text output
```
- Test diagnostic formatting
- Test note inclusion
- Use capsys fixture
- ~20 lines in test_formatters.py

**Test Commit 5: Add JsonlFormatter tests**
```
Add unit tests for JsonlFormatter JSONL output
```
- Test stdout output with capsys
- Test file output with tmp_path
- Test error-only filtering
- ~25 lines in test_formatters.py

### Phase 3: CLI Integration Tests

**Test Commit 6: Add CLI argument parsing tests**
```
Add tests for new CLI arguments parsing
```
- Test --output-format choices
- Test --output-file path handling
- Test default values
- ~18 lines in test_cli.py

**Test Commit 7: Add formatter selection tests**
```
Add tests for CLI formatter selection logic
```
- Test text formatter selection (default)
- Test jsonl formatter selection
- Mock formatter creation
- ~20 lines in test_cli.py

**Test Commit 8: Add results return tests**
```
Add tests for refactored check functions returning results
```
- Mock mypy API calls
- Test results object return
- Test exit code handling
- ~22 lines in test_cli.py

### Phase 4: Integration & Edge Case Tests

**Test Commit 9: Add end-to-end JSONL output tests**
```
Add integration tests for complete JSONL workflow
```
- Test with sample mypy output
- Verify JSONL structure
- Test line count matches errors
- ~25 lines in test_integration.py

**Test Commit 10: Add error handling tests**
```
Add tests for error conditions and edge cases
```
- Test file write permissions
- Test empty results
- Test malformed paths
- ~20 lines in test_integration.py

**Test Commit 11: Add multi-directory merge tests**
```
Add tests for JSONL output with merged results
```
- Test combined mode with JSONL
- Test deduplication
- Test sorted output
- ~22 lines in test_integration.py

### Testing Utilities

**Test Commit 12: Add test fixtures and helpers**
```
Add shared test fixtures for mypy output samples
```
- Create fixture for sample diagnostics
- Create fixture for multi-file results
- ~15 lines in conftest.py

## Key Testing Principles

1. **Isolation**: Each component tested independently
2. **Mocking**: Use mocks to avoid file I/O where possible
3. **Fixtures**: Reusable test data and configurations
4. **Coverage**: Test both happy path and error cases
5. **Parametrization**: Use pytest.mark.parametrize for variations

## Test Execution Strategy

```bash
# Run specific test modules during development
uv run pytest tests/test_models.py -v
uv run pytest tests/test_formatters.py -v
uv run pytest tests/test_cli.py -v

# Run with coverage to ensure completeness
uv run pytest --cov=src/dr_cli/typecheck --cov-report=term-missing

# Run integration tests separately (potentially slower)
uv run pytest tests/test_integration.py -v
```

## Sample Test Structure

```python
# Example from test_models.py
def test_diagnostic_to_jsonl_dict():
    """Test MypyDiagnostic JSONL serialization."""
    diagnostic = MypyDiagnostic(
        location=Location(file="test.py", line=10, column=5),
        level=MessageLevel.ERROR,
        message="Name 'foo' is not defined",
        error_code="name-defined"
    )
    
    result = diagnostic.to_jsonl_dict()
    
    assert result == {
        "file": "test.py",
        "line": 10,
        "column": 5,
        "level": "error",
        "message": "Name 'foo' is not defined",
        "error_code": "name-defined"
    }

# Example from test_formatters.py
def test_jsonl_formatter_file_output(tmp_path):
    """Test JsonlFormatter writing to file."""
    results = MypyResults(
        diagnostics=[...],  # Test data
        standalone_notes=[],
        files_checked=1
    )
    
    output_file = tmp_path / "errors.jsonl"
    formatter = JsonlFormatter()
    formatter.format_results(results, output_file)
    
    # Verify file contents
    lines = output_file.read_text().strip().split('\n')
    assert len(lines) == results.error_count
    
    # Verify each line is valid JSON
    for line in lines:
        data = json.loads(line)
        assert "file" in data
        assert "line" in data
        assert "message" in data
```

## Test Data Fixtures

```python
# In conftest.py
@pytest.fixture
def sample_diagnostic():
    """Sample MypyDiagnostic for testing."""
    return MypyDiagnostic(
        location=Location(file="app.py", line=42, column=8),
        level=MessageLevel.ERROR,
        message="Incompatible types in assignment",
        error_code="assignment",
        notes=["Expected str, got int"]
    )

@pytest.fixture
def sample_results(sample_diagnostic):
    """Sample MypyResults with mixed diagnostics."""
    return MypyResults(
        diagnostics=[
            sample_diagnostic,
            MypyDiagnostic(
                location=Location(file="util.py", line=10),
                level=MessageLevel.WARNING,
                message="Unused import",
                error_code="unused-import"
            )
        ],
        standalone_notes=[],
        files_checked=2
    )
```

## Coverage Goals

- Model methods: 100% coverage
- Formatter classes: 100% coverage
- CLI integration: 90%+ coverage (may exclude daemon crash handling)
- Edge cases: All identified error paths tested

This testing plan ensures comprehensive validation of the JSONL output feature while maintaining clean, focused commits that are easy to review.