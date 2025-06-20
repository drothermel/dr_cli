# Parsing Patterns Reference

A collection of patterns and best practices for implementing parsers in Python, extracted from real-world parser implementations.

## Core Parsing Architectures

### Stateful vs Stateless Parsing

**Stateful Parsing** - Parser maintains context between lines:
```python
class StatefulParser:
    def __init__(self):
        self.current_context = None
        self.accumulated_data = []
    
    def parse_line(self, line: str) -> None:
        if self.is_new_context(line):
            self.flush_context()
            self.current_context = self.extract_context(line)
        else:
            self.accumulated_data.append(line)
```

**When to use stateful**: 
- Multi-line constructs (e.g., error + associated notes)
- Contextual information affects parsing
- Need to accumulate related data

**Stateless Parsing** - Each line is independent:
```python
def parse_line(line: str) -> ParsedData | None:
    for pattern in PATTERNS:
        if match := pattern.match(line):
            return extract_data(match)
    return None
```

**When to use stateless**:
- Each line is self-contained
- No relationship between lines
- Simple log formats

## Regex Pattern Safety

### Handling Optional Groups

**Problem**: Not all regex groups may be present in matches.

```python
# DANGEROUS: Assumes group exists
column = int(match.group("column")) if match.group("column") else None

# SAFE: Check group existence first
groupdict = match.groupdict()
column = int(groupdict["column"]) if "column" in groupdict and groupdict["column"] else None

# CLEANER: Use dict.get()
column_str = match.groupdict().get("column")
column = int(column_str) if column_str else None
```

### Pattern Composition

Build complex patterns from simpler ones:
```python
# Base components
FILE_PATTERN = r"(?P<file>[^:]+)"
LINE_PATTERN = r"(?P<line>\d+)"
COLUMN_PATTERN = r"(?:(?P<column>\d+):)?"  # Optional column

# Composed pattern
LOCATION_PATTERN = f"^{FILE_PATTERN}:{LINE_PATTERN}:{COLUMN_PATTERN}"
```

### Named Groups Contract

When supporting custom patterns, document required group names:
```python
@dataclass
class PatternContract:
    """Required named groups for custom patterns."""
    required_groups = ["file", "line", "level", "message"]
    optional_groups = ["column", "error_code", "end_line", "end_column"]
    
    def validate_pattern(self, pattern: re.Pattern) -> bool:
        # Check pattern has required groups
        test_match = pattern.match(self.sample_line)
        if not test_match:
            return False
        groups = test_match.groupdict()
        return all(g in groups for g in self.required_groups)
```

## Error Handling Strategies

### Parse Errors as Data

Instead of raising exceptions, collect unparseable lines:
```python
@dataclass
class ParseError:
    line_number: int
    line_content: str
    reason: str | None = None

class Parser:
    def __init__(self):
        self.parse_errors: list[ParseError] = []
    
    def parse_line(self, line_num: int, line: str) -> ParsedData | None:
        try:
            return self._try_parse(line)
        except Exception as e:
            self.parse_errors.append(
                ParseError(line_num, line, str(e))
            )
            return None
```

**Benefits**:
- Parser continues on errors
- Users can debug problematic input
- Preserves line numbers for correlation

### Graceful Degradation

Provide fallback behavior for partial matches:
```python
def parse_with_fallback(line: str) -> dict[str, Any]:
    # Try full pattern
    if match := FULL_PATTERN.match(line):
        return extract_full_data(match)
    
    # Try simplified pattern
    if match := SIMPLE_PATTERN.match(line):
        return extract_basic_data(match)
    
    # Return minimal info
    return {"raw_line": line, "parsed": False}
```

## Configuration Patterns

### Parser Configuration

Make parsers adaptable without code changes:
```python
@dataclass
class ParserConfig:
    # Feature flags
    strict_mode: bool = False
    collect_errors: bool = True
    debug: bool = False
    
    # Customization
    custom_patterns: dict[str, re.Pattern] | None = None
    ignore_patterns: list[re.Pattern] | None = None
    
    # Output control
    max_errors: int | None = None
    include_raw_lines: bool = False
```

### Factory Methods for Common Cases

```python
class Parser:
    @classmethod
    def create_strict(cls) -> "Parser":
        """Parser that raises on first error."""
        return cls(ParserConfig(strict_mode=True, collect_errors=False))
    
    @classmethod
    def create_lenient(cls) -> "Parser":
        """Parser that handles malformed input gracefully."""
        return cls(ParserConfig(strict_mode=False, max_errors=None))
    
    @classmethod
    def create_debug(cls) -> "Parser":
        """Parser with debug output enabled."""
        return cls(ParserConfig(debug=True, include_raw_lines=True))
```

## Clean Code Patterns

### Walrus Operator for Parsing Logic

Use `:=` for cleaner conditional parsing:
```python
def parse_line(self, line: str) -> None:
    # Clean cascading pattern matching
    if error := self._try_parse_error(line):
        self.errors.append(error)
    elif warning := self._try_parse_warning(line):
        self.warnings.append(warning)
    elif note := self._try_parse_note(line):
        self.handle_note(note)
    else:
        self.unparsed.append(line)
```

### Match Result Types

Use NamedTuple or dataclass for structured results:
```python
class MatchResult(NamedTuple):
    """Structured result from pattern matching."""
    file: str
    line: int
    column: int | None
    level: str
    message: str
    
    @classmethod
    def from_match(cls, match: re.Match) -> "MatchResult":
        groups = match.groupdict()
        return cls(
            file=groups["file"],
            line=int(groups["line"]),
            column=int(groups["column"]) if groups.get("column") else None,
            level=groups["level"],
            message=groups["message"]
        )
```

## Testing Strategies

### Test Data Organization

Structure test data for clarity:
```python
# Group related test cases
VALID_ERROR_LINES = [
    ("file.py:10: error: Message [code]", "file.py", 10, "error"),
    ("file.py:10:5: error: Message [code]", "file.py", 10, "error"),
]

INVALID_LINES = [
    "No pattern here",
    "file.py: missing line number",
    "10: missing filename",
]

@pytest.mark.parametrize("line,expected_file,expected_line,expected_level", VALID_ERROR_LINES)
def test_parse_valid_errors(line, expected_file, expected_line, expected_level):
    result = parse_error_line(line)
    assert result.file == expected_file
    assert result.line == expected_line
    assert result.level == expected_level
```

### Multi-line String Gotchas

Be careful with line numbering in tests:
```python
# BAD: Empty first line throws off line numbers
test_input = """
Line 1
Line 2"""  # Line 1 is actually empty!

# GOOD: Start content immediately
test_input = """Line 1
Line 2"""

# ALSO GOOD: Use list for explicit control
test_lines = [
    "Line 1",
    "Line 2",
]
```

### Debug Mode Testing

Test debug output systematically:
```python
def test_debug_output(capsys):
    parser = Parser(debug=True)
    parser.parse("test line")
    
    captured = capsys.readouterr()
    assert "[DEBUG]" in captured.out
    assert "test line" in captured.out
```

## Performance Considerations

### Line Processing

For large files, consider:
```python
def parse_file_streaming(filepath: Path) -> ParseResults:
    """Process file line by line without loading into memory."""
    results = ParseResults()
    
    with open(filepath) as f:
        for line_num, line in enumerate(f, start=1):
            if line_num % 10000 == 0:
                logger.info(f"Processed {line_num} lines")
            
            results.add(parse_line(line.rstrip("\n")))
    
    return results
```

### Pattern Compilation

Compile patterns once:
```python
# At module level
ERROR_PATTERN = re.compile(r"...")
WARNING_PATTERN = re.compile(r"...")

# Not in function
def parse_line(line: str):
    # BAD: Recompiles every call
    if re.match(r"...", line):
        pass
```

### Batch Processing

Process multiple lines efficiently:
```python
def parse_lines_batch(lines: list[str]) -> list[ParsedData]:
    # Pre-compile all patterns
    patterns = [re.compile(p) for p in PATTERN_STRINGS]
    
    # Process in batches
    results = []
    for batch in chunks(lines, 1000):
        batch_results = [parse_line(line) for line in batch]
        results.extend(batch_results)
    
    return results
```

## Common Pitfalls

1. **Assuming all groups exist** - Always check optional groups
2. **Forgetting line ending handling** - Strip `\n` consistently  
3. **Not preserving line numbers** - Use `enumerate(lines, start=1)`
4. **Over-broad patterns** - Be specific to avoid false matches
5. **Stateful bugs** - Reset state between parse operations
6. **Unicode handling** - Test with non-ASCII input

## Format Detection

Implement auto-detection for format variations:
```python
def detect_format(sample: str) -> FormatConfig:
    """Detect format from sample output."""
    config = FormatConfig()
    
    # Check for column numbers
    if re.search(r'\S+:\d+:\d+:\s*(error|warning)', sample):
        config.has_columns = True
    
    # Check for error codes
    if re.search(r'\[[\w-]+\]$', sample, re.MULTILINE):
        config.has_error_codes = True
    
    # Check for severity levels
    if re.search(r':\s*warning:', sample):
        config.has_warnings = True
    
    return config
```

## Summary

Key principles for robust parsing:
1. **Fail gracefully** - Collect errors as data
2. **Check groups exist** - Use `groupdict()` for safety
3. **Make it configurable** - Support different formats
4. **Test edge cases** - Empty lines, Unicode, malformed input
5. **Provide debug mode** - Help users troubleshoot
6. **Use modern Python** - Walrus operator, type hints, dataclasses