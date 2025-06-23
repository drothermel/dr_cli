# JSONL Output Combined Implementation & Testing Plan

## Overview
Interleaved implementation and testing plan for adding JSONL output format to dr_cli typecheck command. Each implementation commit is immediately followed by its corresponding test commit, ensuring continuous verification.

## Implementation & Testing Sequence

### Phase 1: Model Enhancements

**Commit 1: Add JSONL serialization to MypyDiagnostic**
```
Add to_jsonl_dict method to MypyDiagnostic for error serialization
```
- Add method to convert diagnostic to flat dict (no notes)
- ~10 lines in models.py

**Commit 2: Add unit tests for MypyDiagnostic JSONL serialization**
```
Add unit tests for MypyDiagnostic JSONL serialization
```
- Test basic error serialization
- Test with/without column numbers
- Test error codes handling
- ~20 lines in test_models.py
- **Run**: `uv run pytest tests/test_models.py::test_diagnostic_to_jsonl_dict -v`

**Commit 3: Add error JSONL export to MypyResults**
```
Add write_errors_as_jsonl method to MypyResults model
```
- Add method to write errors to JSONL file
- Uses existing `errors` computed property
- ~12 lines in models.py

**Commit 4: Add unit tests for MypyResults JSONL file writing**
```
Add unit tests for MypyResults JSONL file writing
```
- Test file creation and content
- Test filtering (errors only, no warnings/notes)
- Use tmp_path fixture
- ~22 lines in test_models.py
- **Run**: `uv run pytest tests/test_models.py::test_results_write_errors_as_jsonl -v`

### Phase 2: Output Abstraction Layer

**Commit 5: Create formatters module with base OutputFormatter**
```
Create formatters module with OutputFormatter abstract base class
```
- New file: formatters.py
- Define ABC with format_results method
- ~15 lines

**Commit 6: Add tests for OutputFormatter abstract base class**
```
Add tests for OutputFormatter abstract base class
```
- Test ABC enforcement
- Test subclass requirements
- ~15 lines in test_formatters.py
- **Run**: `uv run pytest tests/test_formatters.py::test_output_formatter_abc -v`

**Commit 7: Implement TextFormatter for current output behavior**
```
Add TextFormatter to preserve existing text output behavior
```
- Implement format_results for text output
- Move existing print logic here
- ~20 lines in formatters.py

**Commit 8: Add unit tests for TextFormatter text output**
```
Add unit tests for TextFormatter text output
```
- Test diagnostic formatting
- Test note inclusion
- Use capsys fixture
- ~20 lines in test_formatters.py
- **Run**: `uv run pytest tests/test_formatters.py::test_text_formatter -v`

**Commit 9: Implement JsonlFormatter for JSONL output**
```
Add JsonlFormatter for JSONL error output
```
- Implement format_results for JSONL
- Handle stdout vs file output
- ~18 lines in formatters.py

**Commit 10: Add unit tests for JsonlFormatter JSONL output**
```
Add unit tests for JsonlFormatter JSONL output
```
- Test stdout output with capsys
- Test file output with tmp_path
- Test error-only filtering
- ~25 lines in test_formatters.py
- **Run**: `uv run pytest tests/test_formatters.py::test_jsonl_formatter -v`

### Phase 3: CLI Integration

**Commit 11: Add output format arguments to CLI**
```
Add --output-format and --output-file arguments to CLI
```
- Add argparse arguments
- Import Path for type hints
- ~15 lines in cli.py

**Commit 12: Add tests for new CLI arguments parsing**
```
Add tests for new CLI arguments parsing
```
- Test --output-format choices
- Test --output-file path handling
- Test default values
- ~18 lines in test_cli.py
- **Run**: `uv run pytest tests/test_cli.py::test_cli_argument_parsing -v`

**Commit 13: Refactor check_with_daemon to return MypyResults**
```
Refactor check_with_daemon to return results instead of printing
```
- Change return type to tuple[MypyResults, int]
- Remove print statements (defer to formatter)
- ~20 lines changed in cli.py

**Commit 14: Add tests for check_with_daemon results return**
```
Add tests for check_with_daemon returning results
```
- Mock dmypy API calls
- Test results object return
- Test exit code handling
- ~22 lines in test_cli.py
- **Run**: `uv run pytest tests/test_cli.py::test_check_with_daemon_returns_results -v`

**Commit 15: Refactor check_with_mypy to return MypyResults**
```
Refactor check_with_mypy to return results instead of printing
```
- Mirror changes from check_with_daemon
- Maintain parallel structure
- ~20 lines changed in cli.py

**Commit 16: Add tests for check_with_mypy results return**
```
Add tests for check_with_mypy returning results
```
- Mock mypy API calls
- Test results object return
- Test exit code handling
- ~22 lines in test_cli.py
- **Run**: `uv run pytest tests/test_cli.py::test_check_with_mypy_returns_results -v`

**Commit 17: Wire formatters into main function**
```
Integrate formatters into main for output handling
```
- Create formatter based on args
- Call formatter.format_results
- ~18 lines in cli.py

**Commit 18: Add tests for CLI formatter selection logic**
```
Add tests for CLI formatter selection logic
```
- Test text formatter selection (default)
- Test jsonl formatter selection
- Mock formatter creation
- ~20 lines in test_cli.py
- **Run**: `uv run pytest tests/test_cli.py::test_formatter_selection -v`

### Phase 4: Integration & Polish

**Commit 19: Add test fixtures and helpers**
```
Add shared test fixtures for mypy output samples
```
- Create fixture for sample diagnostics
- Create fixture for multi-file results
- ~15 lines in conftest.py

**Commit 20: Add end-to-end JSONL output tests**
```
Add integration tests for complete JSONL workflow
```
- Test with sample mypy output
- Verify JSONL structure
- Test line count matches errors
- ~25 lines in test_integration.py
- **Run**: `uv run pytest tests/test_integration.py::test_jsonl_output_e2e -v`

**Commit 21: Add error count to JSONL output for summary**
```
Include error count metadata in JSONL output file
```
- Add header/footer line with count
- Useful for validation
- ~10 lines in formatters.py

**Commit 22: Add tests for JSONL metadata output**
```
Add tests for JSONL error count metadata
```
- Test metadata line format
- Test count accuracy
- ~15 lines in test_formatters.py
- **Run**: `uv run pytest tests/test_formatters.py::test_jsonl_metadata -v`

**Commit 23: Handle edge cases and add type annotations**
```
Add proper error handling and complete type annotations
```
- Handle file write errors
- Add missing type hints
- ~15 lines across files

**Commit 24: Add error handling tests**
```
Add tests for error conditions and edge cases
```
- Test file write permissions
- Test empty results
- Test malformed paths
- ~20 lines in test_integration.py
- **Run**: `uv run pytest tests/test_integration.py::test_error_handling -v`

**Commit 25: Add multi-directory merge tests**
```
Add tests for JSONL output with merged results
```
- Test combined mode with JSONL
- Test deduplication
- Test sorted output
- ~22 lines in test_integration.py
- **Run**: `uv run pytest tests/test_integration.py::test_multi_directory_jsonl -v`

## Verification Strategy

After each pair of commits:
1. Run the specific test mentioned to verify the implementation
2. Run linting: `uv run ruff check src/dr_cli/typecheck/`
3. Run type checking: `uv run python scripts/typecheck.py src/dr_cli/typecheck/`

After each phase:
1. Run all tests for that component: `uv run pytest tests/test_<component>.py -v`
2. Check coverage: `uv run pytest --cov=src/dr_cli/typecheck --cov-report=term-missing`

## Final Verification

```bash
# Full test suite
uv run pytest

# Coverage report
uv run pytest --cov=src/dr_cli/typecheck --cov-report=html

# Manual testing
echo 'x: int = "string"' > test.py
uv run python -m dr_cli.typecheck test.py --output-format jsonl
uv run python -m dr_cli.typecheck test.py --output-format jsonl --output-file errors.jsonl
cat errors.jsonl | jq .
```

## Benefits of Interleaved Approach

1. **Immediate verification**: Each feature is tested as soon as it's implemented
2. **Catch issues early**: Problems are found before building on top of them
3. **Maintain confidence**: Always have passing tests at each step
4. **Clear progress**: Each pair represents a complete, tested feature
5. **Easy rollback**: Can stop at any commit pair with working code

## Commit Pairing Summary

- Implementation commits: 13 total
- Test commits: 12 total
- Total commits: 25
- Average lines per commit: ~18
- All commits maintain working, tested state