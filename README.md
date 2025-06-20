# dr_cli

A Python library for parsing and analyzing mypy type checker output, built with Pydantic for robust data handling.

## Features

- **Structured Output Parsing**: Convert mypy's text output into structured Pydantic models
- **Error Collection**: Gracefully handle unparseable lines without stopping
- **Flexible Configuration**: Support different mypy output formats (with/without columns)
- **Custom Patterns**: Override regex patterns for non-standard formats
- **Debug Mode**: Built-in debugging to troubleshoot parsing issues
- **Type-Safe**: Full type annotations with strict mypy checking

## Installation

```bash
# Using uv (recommended)
uv add dr_cli

# Using pip
pip install dr_cli
```

## Quick Start

```python
from dr_cli.typecheck.parser import MypyOutputParser

# Create parser
parser = MypyOutputParser()

# Parse mypy output
output = """
src/module.py:42:13: error: Argument 1 has incompatible type "str"; expected "int"  [arg-type]
src/module.py:43:13: note: See documentation for more info
Found 1 error in 1 file (checked 10 source files)
"""

results = parser.parse_output(output)

# Access structured data
print(f"Errors: {results.error_count}")
print(f"Files with errors: {results.files_with_errors}")

for error in results.errors:
    print(f"{error.location.file}:{error.location.line} - {error.message}")
```

## Using MypyOutputParser

### Basic Usage

The parser converts mypy text output into structured Pydantic models:

```python
from dr_cli.typecheck.parser import MypyOutputParser
from dr_cli.typecheck.models import MypyResults

parser = MypyOutputParser()
results: MypyResults = parser.parse_output(mypy_output_text)

# Access parsed data
errors = results.errors              # List of error diagnostics
warnings = results.warnings          # List of warning diagnostics
files_checked = results.files_checked # Number of files mypy checked
parse_errors = results.parse_errors  # Lines that couldn't be parsed
```

### Configuration Options

#### Different mypy Output Formats

```python
from dr_cli.typecheck.parser import MypyOutputParser, ParserConfig

# For mypy without column numbers (--no-column-numbers)
parser = MypyOutputParser.create_with_minimal_output()

# For mypy with all features (--show-column-numbers --show-error-end)
parser = MypyOutputParser.create_with_full_output()

# Custom configuration
config = ParserConfig(
    show_column_numbers=True,
    show_error_end=False,
    debug=True  # Enable debug output
)
parser = MypyOutputParser(config)
```

#### Automatic Format Detection

Let the parser detect the format from sample output:

```python
# Detect format from sample
sample = "file.py:10:5: error: Message [code]"
config = MypyOutputParser.detect_format(sample)
parser = MypyOutputParser(config)
```

### Debug Mode

Enable debug mode to troubleshoot parsing issues:

```python
config = ParserConfig(debug=True)
parser = MypyOutputParser(config)

results = parser.parse_output(output)
# Prints:
# [DEBUG] Line 1: Parsed as diagnostic
# [DEBUG] Line 2: Parsed as note
# [DEBUG] Line 3: No pattern matched - 'content'
```

### Custom Pattern Override

For non-standard mypy output formats, provide custom regex patterns:

```python
import re
from dr_cli.typecheck.parser import ParserConfig

# Custom format: "ERROR in file.py at 42: Message"
custom_diagnostic = re.compile(
    r"^(?P<level>ERROR|WARNING) in (?P<file>[^:]+) "
    r"at (?P<line>\d+): (?P<message>.*)$"
)

config = ParserConfig(custom_diagnostic_pattern=custom_diagnostic)
parser = MypyOutputParser(config)
```

**Required group names for custom patterns:**
- `file` - Source file path
- `line` - Line number (required)
- `column` - Column number (optional)
- `level` - Message level (error/warning/note)
- `message` - The diagnostic message
- `error_code` - Mypy error code (optional)

### Parse Error Handling

The parser collects unparseable lines instead of failing:

```python
results = parser.parse_output(output)

for error in results.parse_errors:
    print(f"Line {error.line_number}: {error.line_content}")
    print(f"Reason: {error.reason}")
```

### Working with Results

The `MypyResults` model provides convenient properties:

```python
results = parser.parse_output(output)

# Counts
print(f"Total errors: {results.error_count}")
print(f"Total warnings: {results.warning_count}")

# Files with issues
for file in results.files_with_errors:
    print(f"File with errors: {file}")

# Formatted summary
print(results.format_summary())
# Output: "Found 3 errors in 2 files (checked 10 source files)"

# Access individual diagnostics
for diag in results.diagnostics:
    print(f"{diag.location.file}:{diag.location.line} "
          f"{diag.level.value}: {diag.message} [{diag.error_code}]")
    
    # Associated notes
    for note in diag.notes:
        print(f"  Note: {note}")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/dr_cli.git
cd dr_cli

# Install dependencies with uv
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test
uv run pytest tests/test_parser.py -xvs
```

### Code Quality

```bash
# Run linting
uv run ruff check

# Fix linting issues
uv run ruff check --fix

# Format code
uv run ruff format

# Type checking
uv run python scripts/typecheck.py
```

## License

MIT License - see LICENSE file for details.