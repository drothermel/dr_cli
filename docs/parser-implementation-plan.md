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

#### Commit 1: "Add regex patterns and parse utilities"
- Define all regex patterns as constants in parser.py
- Create utility functions for regex matching
- Add type hints for match results

### Phase 2: Core Parser Implementation

#### Commit 2: "Add parser initialization and base structure"
- Create `MypyOutputParser` class
- Add `__init__()` with basic fields
- Instance variables for state tracking
- Import statements and class docstring

#### Commit 3: "Add diagnostic parsing method"
- Implement `_try_parse_diagnostic()` method
- Regex matching for errors/warnings
- Create MypyDiagnostic instances from matches

#### Commit 4: "Add note parsing with state tracking"
- Implement `_try_parse_note()` method
- Logic to associate notes with previous diagnostic
- Handle standalone notes separately

#### Commit 5: "Add summary line parsing"
- Implement `_try_parse_summary()` method
- Extract file counts from summary
- Store in parser state

#### Commit 6: "Implement main parse_output method"
- Add `parse_output()` method that orchestrates parsing
- Line-by-line processing loop
- Return MypyResults instance

### Phase 3: Error Handling and Robustness

#### Commit 7: "Add ParseError model"
- Create ParseError dataclass in models.py
- Add parse_errors field to MypyResults
- Update model docstrings

#### Commit 8: "Add line tracking and error collection"
- Track line numbers during parsing
- Collect unparseable lines
- Create ParseError instances for failed parses

#### Commit 9: "Add debug logging support"
- Optional logging for parse attempts
- Log pattern matches/failures
- Configurable verbosity level

### Phase 4: Configuration and Extensibility

#### Commit 10: "Add parser configuration options"
- Configuration for show_column_numbers flag
- Configuration for show_error_end flag
- Pattern selection based on configuration

#### Commit 11: "Add custom pattern support"
- Allow custom regex patterns
- Pattern override mechanism
- Extensibility for special cases

#### Commit 12: "Add output format helpers"
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

## Current Status
- Phase 1: Not started
- Phase 2: Not started
- Phase 3: Not started
- Phase 4: Not started

Last updated: 2025-01-19