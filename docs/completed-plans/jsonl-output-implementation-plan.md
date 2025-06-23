# JSONL Output Implementation Plan

## Overview
Add JSONL output format to dr_cli typecheck command for machine-readable error reporting.

## Implementation Sequence

### Phase 1: Foundation (Model Enhancements)

**Commit 1: Add JSONL serialization to MypyDiagnostic**
```
Add to_jsonl_dict method to MypyDiagnostic for error serialization
```
- Add method to convert diagnostic to flat dict (no notes)
- ~10 lines in models.py

**Commit 2: Add error JSONL export to MypyResults**  
```
Add write_errors_as_jsonl method to MypyResults model
```
- Add method to write errors to JSONL file
- Uses existing `errors` computed property
- ~12 lines in models.py

### Phase 2: Output Abstraction Layer

**Commit 3: Create formatters module with base OutputFormatter**
```
Create formatters module with OutputFormatter abstract base class
```
- New file: formatters.py
- Define ABC with format_results method
- ~15 lines

**Commit 4: Implement TextFormatter for current output behavior**
```
Add TextFormatter to preserve existing text output behavior
```
- Implement format_results for text output
- Move existing print logic here
- ~20 lines in formatters.py

**Commit 5: Implement JsonlFormatter for JSONL output**
```
Add JsonlFormatter for JSONL error output
```
- Implement format_results for JSONL
- Handle stdout vs file output
- ~18 lines in formatters.py

### Phase 3: CLI Integration

**Commit 6: Add output format arguments to CLI**
```
Add --output-format and --output-file arguments to CLI
```
- Add argparse arguments
- Import Path for type hints
- ~15 lines in cli.py

**Commit 7: Refactor check_with_daemon to return MypyResults**
```
Refactor check_with_daemon to return results instead of printing
```
- Change return type to tuple[MypyResults, int]
- Remove print statements (defer to formatter)
- ~20 lines changed in cli.py

**Commit 8: Refactor check_with_mypy to return MypyResults**
```
Refactor check_with_mypy to return results instead of printing
```
- Mirror changes from check_with_daemon
- Maintain parallel structure
- ~20 lines changed in cli.py

**Commit 9: Wire formatters into main function**
```
Integrate formatters into main for output handling
```
- Create formatter based on args
- Call formatter.format_results
- ~18 lines in cli.py

### Phase 4: Polish & Enhancement

**Commit 10: Add error count to JSONL output for summary**
```
Include error count metadata in JSONL output file
```
- Add header/footer line with count
- Useful for validation
- ~10 lines in formatters.py

**Commit 11: Handle edge cases and add type annotations**
```
Add proper error handling and complete type annotations
```
- Handle file write errors
- Add missing type hints
- ~15 lines across files

## Key Design Decisions

1. **Incremental Refactoring**: Each commit maintains working functionality
2. **Separation of Concerns**: Formatters isolated from checking logic
3. **Parallel Structure**: check_with_daemon and check_with_mypy refactored identically
4. **Backwards Compatible**: Default behavior unchanged
5. **Testable Units**: Each commit adds a complete, testable feature

## Usage Examples

```bash
# Output errors to console in JSONL format
uv run python -m dr_cli.typecheck --output-format jsonl src/ tests/

# Save errors to file
uv run python -m dr_cli.typecheck --output-format jsonl --output-file errors.jsonl src/ tests/

# Process with standard tools
uv run python -m dr_cli.typecheck --output-format jsonl src/ | jq '.file' | sort | uniq -c
```