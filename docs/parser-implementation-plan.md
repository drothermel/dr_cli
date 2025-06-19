# MypyOutputParser Implementation Plan

## Overview
This document outlines the commit sequence for implementing the MypyOutputParser. Each commit adds a specific piece of functionality, following the principle of small, focused changes.

## Completed Commits
- ✅ Create typecheck package structure
- ✅ Add core types: MessageLevel enum and Location model
- ✅ Add mypy message models with validation
- ✅ Add MypyResults model with computed properties

## Upcoming Commits

### Phase 1: Parsing Foundation

#### Commit 1: "Add mypy output regex patterns and parsing utilities"
- Define all regex patterns as constants in parser.py
- Create utility functions for regex matching
- Add type hints for match results

### Phase 2: Core Parser Implementation

#### Commit 2: "Add MypyOutputParser class with initialization"
- Create `MypyOutputParser` class
- Add `__init__()` with basic fields
- Instance variables for state tracking
- Import statements and class docstring

#### Commit 3: "Add diagnostic parsing method for errors and warnings"
- Implement `_try_parse_diagnostic()` method
- Regex matching for errors/warnings
- Create MypyDiagnostic instances from matches

#### Commit 4: "Add note parsing with diagnostic association"
- Implement `_try_parse_note()` method
- Logic to associate notes with previous diagnostic
- Handle standalone notes separately

#### Commit 5: "Add summary line parsing for file counts"
- Implement `_try_parse_summary()` method
- Extract file counts from summary
- Store in parser state

#### Commit 6: "Add main parse_output method with line processing"
- Add `parse_output()` method that orchestrates parsing
- Line-by-line processing loop
- Return MypyResults instance

### Phase 3: Error Handling and Robustness

#### Commit 7: "Add ParseError model for unparseable lines"
- Create ParseError dataclass in models.py
- Add parse_errors field to MypyResults
- Update model docstrings

#### Commit 8: "Add line tracking and parse error collection"
- Track line numbers during parsing
- Collect unparseable lines
- Create ParseError instances for failed parses

#### Commit 9: "Add optional debug logging for parsing"
- Optional logging for parse attempts
- Log pattern matches/failures
- Configurable verbosity level

### Phase 4: Configuration and Extensibility

#### Commit 10: "Add parser configuration for mypy output formats"
- Configuration for show_column_numbers flag
- Configuration for show_error_end flag
- Pattern selection based on configuration

#### Commit 11: "Add custom regex pattern override support"
- Allow custom regex patterns
- Pattern override mechanism
- Extensibility for special cases

#### Commit 12: "Add format detection and auto-configuration helpers"
- Helper methods for different mypy configurations
- Format detection from output
- Auto-configuration support

## Implementation Notes

### Estimated Lines per Commit
- Commit 1: ~30 lines (patterns + utilities)
- Commit 2: ~15 lines (class definition + init)
- Commit 3: ~20 lines (one parsing method)
- Commit 4: ~25 lines (note parsing with state)
- Commit 5: ~10 lines (simple summary parsing)
- Commit 6: ~15 lines (orchestration method)
- Commit 7: ~15 lines (model additions)
- Commit 8: ~20 lines (error tracking)
- Commit 9: ~15 lines (logging setup)
- Commit 10: ~20 lines (configuration)
- Commit 11: ~15 lines (custom patterns)
- Commit 12: ~20 lines (format helpers)

### Key Principles
1. Each commit is independently testable
2. Commits build on each other logically
3. No commit breaks existing functionality
4. Clear, descriptive commit messages
5. Minimal lines per commit for easy review

### Testing Strategy
- After Phase 2: Basic parsing should work
- After Phase 3: Robust error handling  
- After Phase 4: Full feature set

### Implementation Insights (From Testing Phase)
- **Test each commit incrementally**: Don't wait until full implementation
- **Use parametrized tests**: For testing multiple regex patterns and mypy output formats
- **Test with real mypy output**: Include actual mypy output samples in test fixtures
- **Focus on edge cases**: Empty output, malformed lines, unicode characters in filenames
- **State tracking is critical**: Notes must be properly associated with their parent diagnostics
- **Regex debugging**: Log pattern matches during development to debug parsing issues

### Key Learnings Applied
- **Pydantic computed fields**: Remember `@computed_field` decorator for any properties that should serialize
- **Error message testing**: Use `'expected' in error['msg']` not exact equality
- **Small commits work**: 20-30 line commits made testing implementation very manageable
- **TodoWrite integration**: Use TodoWrite to track progress through all 12 commits
- **Documentation updates**: Update docs/mypy-reference.md with any new parsing insights discovered

## Current Status
- Phase 1: Not started
- Phase 2: Not started
- Phase 3: Not started
- Phase 4: Not started

Last updated: 2025-01-19