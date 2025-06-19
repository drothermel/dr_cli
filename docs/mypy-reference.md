# Mypy Reference

## Output Format

### Message Structure
```
<file>:<line>:<column>: <severity>: <message> [<error-code>]
```

Example:
```
src/module.py:42:13: error: Argument 1 has incompatible type "str"; expected "int"  [arg-type]
src/module.py:42:13: note: See https://mypy.rtfd.io/en/stable/_refs.html#code-arg-type for more info
```

### Severity Types
- `error:` - Type checking violations
- `warning:` - Deprecation warnings and less severe issues  
- `note:` - Supplementary context for preceding error/warning

### Message Grouping
- Notes always follow their associated error/warning
- Notes provide additional context, suggestions, or documentation links
- Notes do not affect exit codes

## Python API

### Import
```python
from mypy import api
from typing import Tuple, List
```

### Functions

#### `api.run(args: List[str]) -> Tuple[str, str, int]`
- **Returns**: `(stdout, stderr, exit_status)`
- **stdout**: Type checking results (errors, warnings, notes)
- **stderr**: System-level errors
- **exit_status**: 0 (success), 1 (type errors), 2 (system error)
- **Thread-safe**: Yes

#### `api.run_dmypy(args: List[str]) -> Tuple[str, str, int]`
- **Returns**: Same as `api.run()`
- **Uses**: dmypy daemon for incremental checking
- **Thread-safe**: No (modifies sys.stdout/stderr)
- **Performance**: Faster for repeated runs

### dmypy Commands
```python
api.run_dmypy(["start"])          # Start daemon
api.run_dmypy(["status"])         # Check daemon status
api.run_dmypy(["check", "path"]) # Type check files
api.run_dmypy(["stop"])          # Stop daemon
api.run_dmypy(["restart"])       # Restart daemon
```

## Command-Line Options

### Output Control
- `--show-error-codes` - Display error codes in brackets (default)
- `--hide-error-codes` - Hide error codes
- `--show-column-numbers` - Include column numbers
- `--show-error-end` - Show end position (line:column)
- `--pretty` - Pretty output with source snippets
- `--show-error-context` - Additional context in messages

### Output Format Components
1. File path (relative or absolute)
2. Line number (always shown)
3. Column number (optional)
4. End position (optional with `--show-error-end`)
5. Severity (`error:`, `warning:`, `note:`)
6. Message text
7. Error code in brackets (optional)

## Exit Codes
- **0**: No type errors found
- **1**: Type errors detected
- **2**: Fatal/system error

## Summary Line Format
```
Found <X> errors in <Y> files (checked <Z> source files)
```

## Daemon Behavior
- Caches type information between runs
- Must restart on configuration changes
- Can crash on certain errors (handle with retry logic)
- Status codes: 0 (running), 1 (not running)