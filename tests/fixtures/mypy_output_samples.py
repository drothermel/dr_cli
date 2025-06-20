"""Real mypy output samples for testing."""

# Single error output
SIMPLE_ERROR_OUTPUT = """tests/fixtures/sample_code/simple_error.py:10: error: Argument 1 to "add_numbers" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)"""

# Multiple errors in same file
MULTIPLE_ERRORS_OUTPUT = """tests/fixtures/sample_code/multiple_errors.py:10: error: Name "undefined_variable" is not defined  [name-defined]
tests/fixtures/sample_code/multiple_errors.py:13: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
tests/fixtures/sample_code/multiple_errors.py:16: error: Argument 1 to "greet" has incompatible type "int"; expected "str"  [arg-type]
Found 3 errors in 1 file (checked 1 source file)"""

# Errors with notes (multiple list items)
ERROR_WITH_NOTES_OUTPUT = """tests/fixtures/sample_code/error_with_notes.py:13: error: List item 0 has incompatible type "int"; expected "str"  [list-item]
tests/fixtures/sample_code/error_with_notes.py:13: error: List item 1 has incompatible type "int"; expected "str"  [list-item]
tests/fixtures/sample_code/error_with_notes.py:13: error: List item 2 has incompatible type "int"; expected "str"  [list-item]
Found 3 errors in 1 file (checked 1 source file)"""

# Multi-file project output
MULTI_FILE_OUTPUT = """tests/fixtures/sample_code/multi_file_project/file_a.py:10: error: Argument 1 to "calculate" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 2 source files)"""

# Empty output (no errors)
EMPTY_OUTPUT = """Success: no issues found in 1 source file"""

# Multiple files checked, no errors
MULTI_FILE_EMPTY = """Success: no issues found in 2 source files"""

# Error with notes (overload)
ERROR_WITH_NOTES_OVERLOAD = """tests/fixtures/sample_code/overload_error.py:12: error: Function is missing a type annotation  [no-untyped-def]
tests/fixtures/sample_code/overload_error.py:20: error: No overload variant of "process" matches argument type "list[int]"  [call-overload]
tests/fixtures/sample_code/overload_error.py:20: note: Possible overload variants:
tests/fixtures/sample_code/overload_error.py:20: note:     def process(x: int) -> str
tests/fixtures/sample_code/overload_error.py:20: note:     def process(x: str) -> int
Found 2 errors in 1 file (checked 1 source file)"""