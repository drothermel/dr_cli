# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Essential Commands
- `uv sync` - Install/update dependencies (dev and test groups)
- `uv run ruff check` - Run linting
- `uv run ruff format` - Format code
- `uv run python scripts/typecheck.py` - Run type checking with dmypy daemon
- `uv run pytest` - Run tests with parallel execution and coverage

### Type Checking Script
The project includes a custom `scripts/typecheck.py` that wraps mypy with dmypy daemon support:
- Default: Uses dmypy daemon for faster incremental checking
- `--no-daemon`: Falls back to regular mypy
- `--restart`: Restart daemon before checking
- `--stop`: Stop daemon
- Automatically handles daemon crashes and restarts

### Testing
- Uses pytest with parallel execution (`-n auto`)
- Includes coverage reporting, timeout handling, and mocking
- Test markers: `slow`, `serial`, `integration`
- ML-specific testing utilities available via `test-ml` dependency group

## Architecture

This is a Python library project using modern tooling:

### Project Structure
- `src/dr_cli/` - Main package with typed interface (`py.typed`)
- `scripts/` - Utility scripts including advanced type checking
- Uses `uv` for dependency management with lockfile
- Configured for ML/data science development patterns

### Code Quality Configuration
- **Ruff**: Extensive linting rules optimized for ML code with 88-char line length
- **MyPy**: Strict type checking with explicit package bases
- **PyTest**: Parallel testing with comprehensive test discovery
- **Coverage**: Excludes debug/visualization code and GPU-specific branches

### Development Patterns
- Type hints required on all functions
- Assertions preferred over exceptions (ML performance requirement)
- Google-style docstrings
- Supports ML-specific patterns (higher complexity thresholds, boolean parameters)

## Dependencies

### Core Groups
- `dev`: mypy, ruff, tomlkit
- `test`: pytest with extensions (cov, xdist, timeout, mock, benchmark)
- `test-ml`: PyTorch testing utilities
- `all`: Includes dev and test groups

### Package Management
- Uses `uv` with lockfile for reproducible environments
- Development dependencies clearly separated from runtime
- Optional ML testing dependencies for specialized use cases