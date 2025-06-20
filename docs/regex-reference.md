# Regex Reference

A focused guide to Python regex patterns, with emphasis on common pain points and safe practices.

## Python Regex Basics

### Raw Strings
Always use raw strings for regex patterns to avoid escaping issues:
```python
# BAD: Double escaping needed
pattern = "\\d+\\.\\d+"

# GOOD: Raw string
pattern = r"\d+\.\d+"

# GOOD: Even better with re.compile
pattern = re.compile(r"\d+\.\d+")
```

### Compilation
Compile patterns for reuse:
```python
# At module level for best performance
EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Use throughout code
if EMAIL_PATTERN.match(email):
    process_email(email)
```

## Named Groups

### Basic Named Groups
Use `(?P<name>...)` syntax:
```python
# Define pattern with named groups
pattern = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})')

match = pattern.match("2024-01-15")
if match:
    print(match.group("year"))   # "2024"
    print(match.group("month"))  # "01"
    print(match.group("day"))    # "15"
```

### Safe Group Access
**Critical**: Not all groups may be present!

```python
# DANGEROUS - Assumes group exists
value = match.group("optional_group")  # Can raise error!

# SAFE - Check existence first
groups = match.groupdict()
value = groups.get("optional_group")  # Returns None if missing

# SAFE - With default
value = groups.get("optional_group", "default")

# SAFE - Check before access
if "optional_group" in match.groupdict():
    value = match.group("optional_group")
```

### Optional Groups
Make groups optional with `?`:
```python
# Column number is optional
pattern = re.compile(
    r'(?P<file>[^:]+):'
    r'(?P<line>\d+)'
    r'(?::(?P<column>\d+))?'  # Optional :column
)

# Matches both:
# "file.py:10" (column=None)
# "file.py:10:5" (column="5")
```

## Common Patterns

### File Paths
Handle various path formats:
```python
# Basic file path
FILE_PATH = re.compile(r'(?P<path>[\w/\-_.]+\.py)')

# Windows and Unix paths
CROSS_PLATFORM_PATH = re.compile(
    r'(?P<path>(?:[A-Za-z]:)?[\\/]?(?:[\w\-_.]+[\\/])*[\w\-_.]+)'
)

# With line/column
FILE_LOCATION = re.compile(
    r'(?P<file>[^:]+):(?P<line>\d+)(?::(?P<column>\d+))?'
)
```

### Numbers
Parse various number formats:
```python
# Integer (positive/negative)
INTEGER = re.compile(r'(?P<num>-?\d+)')

# Float
FLOAT = re.compile(r'(?P<num>-?\d+\.?\d*)')

# Scientific notation
SCIENTIFIC = re.compile(r'(?P<num>-?\d+\.?\d*[eE][+-]?\d+)')

# With thousands separators
FORMATTED_NUMBER = re.compile(r'(?P<num>-?\d{1,3}(?:,\d{3})*(?:\.\d+)?)')
```

### Quoted Strings
Handle various quote styles:
```python
# Single or double quoted
QUOTED = re.compile(r'''(?P<quote>["'])(?P<content>.*?)(?P=quote)''')

# With escapes
QUOTED_WITH_ESCAPES = re.compile(
    r'''(?P<quote>["'])(?P<content>(?:\\.|(?!(?P=quote)).)*?)(?P=quote)'''
)

# Multi-line strings
MULTILINE = re.compile(r'(?P<quote>"""|' + r"''')(?P<content>.*?)(?P=quote)", re.DOTALL)
```

## Gotchas and Solutions

### Greedy vs Non-Greedy

```python
# GREEDY: Takes as much as possible
pattern = re.compile(r'<.*>')  
# "<tag>content</tag>" matches entire string

# NON-GREEDY: Takes as little as possible  
pattern = re.compile(r'<.*?>')
# "<tag>content</tag>" matches just "<tag>"
```

### Escape Special Characters
Characters that need escaping: `. ^ $ * + ? { } [ ] \ | ( )`

```python
# WRONG: Period matches any character
pattern = re.compile(r'file.py')  # Matches "fileXpy"!

# RIGHT: Escape the period
pattern = re.compile(r'file\.py')

# Use re.escape() for literal strings
filename = "file.py"
pattern = re.compile(re.escape(filename))
```

### Start and End Anchors

```python
# Matches anywhere in string
pattern = re.compile(r'\d+')
# "abc123def" → finds "123"

# Must match entire string
pattern = re.compile(r'^\d+$')
# "abc123def" → no match
# "123" → matches

# Line-by-line with MULTILINE
pattern = re.compile(r'^\d+$', re.MULTILINE)
# "123\nabc\n456" → finds "123" and "456"
```

### Backreferences

Reference previously matched groups:
```python
# Match repeated words
REPEATED_WORD = re.compile(r'\b(?P<word>\w+)\s+(?P=word)\b')
# "the the cat" → matches "the the"

# Match paired tags
HTML_TAG = re.compile(r'<(?P<tag>\w+)>.*?</(?P=tag)>')
# "<div>content</div>" → matches
```

## Performance Tips

### Compile Once
```python
# BAD: Recompiles every time
def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

# GOOD: Compile once
EMAIL_RE = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
def validate_email(email):
    return EMAIL_RE.match(email)
```

### Avoid Catastrophic Backtracking
```python
# DANGEROUS: Can cause exponential time
pattern = re.compile(r'(x+)+y')
# "xxxxxxxxxxxxxxxxx" → very slow!

# SAFER: Atomic grouping (Python 3.11+)
pattern = re.compile(r'(?>x+)+y')

# SAFER: Rewrite pattern
pattern = re.compile(r'x+y')
```

### Use Specific Character Classes
```python
# SLOW: Generic wildcard
pattern = re.compile(r'.*')

# FASTER: Specific classes
pattern = re.compile(r'\w*')    # Word characters
pattern = re.compile(r'[^:]*')  # Everything except colon
```

## Debugging Regex

### Verbose Mode
Use for complex patterns:
```python
pattern = re.compile(r'''
    (?P<protocol>https?)://     # Protocol
    (?P<domain>[\w.-]+)         # Domain name
    (?P<port>:\d+)?             # Optional port
    (?P<path>/[^?#]*)?          # Optional path
    (?P<query>\?[^#]*)?         # Optional query
    (?P<fragment>\#.*)?         # Optional fragment
''', re.VERBOSE)
```

### Test Incrementally
Build patterns step by step:
```python
# Start simple
pattern = r'\d+'

# Add complexity
pattern = r'(?P<num>\d+)'

# Add more
pattern = r'(?P<sign>[+-])?(?P<num>\d+)'

# Final
pattern = r'(?P<sign>[+-])?(?P<num>\d+)(?:\.(?P<decimal>\d+))?'
```

### Online Tools
- [regex101.com](https://regex101.com/) - Interactive testing with Python flavor
- [regexr.com](https://regexr.com/) - Visual regex builder
- [regexpal.com](https://regexpal.com/) - Simple tester

## Common Use Cases

### Log Parsing
```python
# Apache log entry
LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) '
    r'- - '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>\w+) (?P<path>[^ ]+) [^"]+" '
    r'(?P<status>\d+) '
    r'(?P<size>\d+)'
)
```

### Error Message Extraction
```python
# Python traceback
TRACEBACK_FILE = re.compile(
    r'File "(?P<file>[^"]+)", line (?P<line>\d+), in (?P<func>\w+)'
)

# Generic error with code
ERROR_MSG = re.compile(
    r'(?P<level>ERROR|WARNING|INFO): (?P<msg>[^\[]+)'
    r'(?:\[(?P<code>\w+)\])?'
)
```

### Data Validation
```python
# Email validation (simplified)
EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Phone number (US)
US_PHONE = re.compile(r'^\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$')

# URL validation
URL = re.compile(
    r'^https?://'                    # Protocol
    r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+' # Domain
    r'[A-Z]{2,6}'                    # TLD
    r'(?::\d+)?'                     # Port
    r'(?:/[^?#]*)?'                  # Path
    r'(?:\?[^#]*)?'                  # Query
    r'(?:#.*)?$',                    # Fragment
    re.IGNORECASE
)
```

## Best Practices

1. **Always use raw strings** (`r'pattern'`)
2. **Compile patterns once** at module level
3. **Use named groups** for clarity
4. **Check group existence** before access
5. **Be specific** rather than using `.*`
6. **Test with edge cases** (empty, Unicode, very long)
7. **Document complex patterns** with verbose mode
8. **Escape special characters** or use `re.escape()`
9. **Anchor patterns** when matching full strings
10. **Profile performance** for critical paths

## Quick Reference Card

```python
# Anchors
^    # Start of string/line
$    # End of string/line
\b   # Word boundary
\B   # Not word boundary

# Character Classes  
.    # Any character (except newline)
\d   # Digit [0-9]
\D   # Not digit
\w   # Word character [a-zA-Z0-9_]
\W   # Not word character
\s   # Whitespace
\S   # Not whitespace

# Quantifiers
*    # 0 or more
+    # 1 or more  
?    # 0 or 1
{n}  # Exactly n
{n,} # n or more
{n,m}# Between n and m

# Groups
(...)           # Capturing group
(?:...)         # Non-capturing group
(?P<name>...)   # Named group
(?P=name)       # Backreference to named group

# Lookarounds
(?=...)   # Positive lookahead
(?!...)   # Negative lookahead
(?<=...)  # Positive lookbehind  
(?<!...)  # Negative lookbehind

# Flags
re.IGNORECASE   # Case insensitive
re.MULTILINE    # ^ and $ match line boundaries
re.DOTALL       # . matches newline
re.VERBOSE      # Allow comments and whitespace
```