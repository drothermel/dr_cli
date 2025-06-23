# dr_cli

A Python library for parsing and analyzing mypy type checker output, built with Pydantic for robust data handling.

## Features

- **Structured Output Parsing**: Convert mypy's text output into structured Pydantic models
- **Error Collection**: Gracefully handle unparseable lines without stopping
- **Flexible Configuration**: Support different mypy output formats (with/without columns)
- **Custom Patterns**: Override regex patterns for non-standard formats
- **Debug Mode**: Built-in debugging to troubleshoot parsing issues
- **Type-Safe**: Full type annotations with strict mypy checking
- **JSONL Export**: Export errors as JSONL for integration with other tools

## Installation

```bash
# Using uv (recommended)
uv add dr_cli

# Using pip
pip install dr_cli
```

### Installing as a Global Tool

The package includes a global `dr-typecheck` command that can be installed with uv:

```bash
# From this repository
uv tool install .

# Or from a path
uv tool install /path/to/dr_cli

# Upgrade later
uv tool upgrade dr-cli
```

## Using dr-typecheck

The `dr-typecheck` command is an advanced wrapper around mypy that supports both regular mypy and dmypy daemon mode:

```bash
# Check multiple directories
dr-typecheck src scripts tests

# Check current directory
dr-typecheck

# Use regular mypy instead of daemon
dr-typecheck --no-daemon src tests

# Restart daemon before checking
dr-typecheck --restart src

# Stop daemon
dr-typecheck --stop

# Output in JSONL format for integration
dr-typecheck --output-format jsonl src

# Save JSONL output to file
dr-typecheck --output-format jsonl --output-file errors.jsonl src
```

### Features

- **Daemon mode by default**: Uses dmypy for faster incremental type checking
- **Multiple paths**: Check multiple directories in one command
- **Automatic retry**: Handles daemon crashes gracefully
- **Combined mode**: When checking multiple paths, runs each independently and combines results
- **Parser integration**: Uses the mypy output parser to merge results from multiple directories
- **JSONL output**: Export errors in JSONL format for integration with other tools

### Combined Mode

When checking multiple directories, `dr-typecheck` automatically uses combined mode:
- Each directory is checked independently (failures in one don't prevent checking others)
- Results are parsed and merged using the mypy output parser
- A unified summary shows total errors across all directories

Note: dmypy prints status messages like ">> Checking:" that cannot be suppressed. For cleaner output, use `--no-daemon`.

### Output Formats

The `dr-typecheck` command supports multiple output formats:

#### Text Output (Default)
Standard mypy-style text output with diagnostic messages and summary:

```bash
dr-typecheck src/
# Output:
# src/module.py:42:13: error: Incompatible types [assignment]
# Found 1 error in 1 file (checked 10 source files)
```

#### JSONL Output
Export errors as JSON Lines format for integration with other tools:

```bash
# Output to stdout
dr-typecheck --output-format jsonl src/
# Output:
# {"type": "metadata", "error_count": 1}
# {"file": "src/module.py", "line": 42, "column": 13, "level": "error", "message": "Incompatible types", "error_code": "assignment"}

# Save to file
dr-typecheck --output-format jsonl --output-file errors.jsonl src/
```

**JSONL Features:**
- **Errors only**: Excludes warnings and notes for cleaner integration
- **Metadata**: Files include error count as first line for validation
- **Structured**: Each error is a JSON object with consistent fields
- **Tool-friendly**: Easy to process with `jq`, data pipelines, or CI systems

**Example with jq:**
```bash
# Count errors by file
dr-typecheck --output-format jsonl src/ | jq -r 'select(.file) | .file' | sort | uniq -c

# Get errors from specific file
dr-typecheck --output-format jsonl src/ | jq -r 'select(.file == "src/module.py")'
```

### Example Usage in Another Project

```bash
cd /path/to/your/project
dr-typecheck src scripts tests

# For cleaner output without status messages
dr-typecheck --no-daemon src scripts tests
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

### JSONL Export

Export results as JSONL (JSON Lines) format for integration with other tools:

```python
from dr_cli.typecheck.parser import MypyOutputParser
from dr_cli.typecheck.formatters import JsonlFormatter

# Parse mypy output
parser = MypyOutputParser()
results = parser.parse_output(mypy_output)

# Export to JSONL file
formatter = JsonlFormatter()
formatter.format_results(results, "errors.jsonl")

# Or work with individual error dictionaries
for error in results.errors:
    json_dict = error.to_jsonl_dict()
    print(json_dict)
    # Output: {"file": "src/test.py", "line": 10, "column": 5, 
    #          "level": "error", "message": "...", "error_code": "..."}
```

**JSONL Format Details:**
- Each line is a valid JSON object
- First line contains metadata: `{"type": "metadata", "error_count": N}`
- Subsequent lines are error objects with fields: `file`, `line`, `column`, `level`, `message`, `error_code`
- Only errors are included (warnings and notes are excluded)
- Compatible with streaming JSON processors and data pipelines

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

# Type checking (if not installed globally)
uv run python -m dr_cli.typecheck
```

## License

MIT License - see LICENSE file for details.