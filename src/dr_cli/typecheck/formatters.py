"""Output formatters for mypy type checking results."""

from abc import ABC, abstractmethod
from dr_cli.typecheck.models import MypyResults


class OutputFormatter(ABC):
    """Abstract base class for formatting mypy results."""

    @abstractmethod
    def format_results(
        self, results: MypyResults, output_path: str | None = None
    ) -> None:
        """Format and output the mypy results.

        Args:
            results: The mypy results to format
            output_path: Optional path for file output
        """


class TextFormatter(OutputFormatter):
    """Formatter for standard text output (preserves existing behavior)."""

    def format_results(
        self, results: MypyResults, output_path: str | None = None
    ) -> None:
        """Format results as text output to stdout."""
        # output_path is ignored for text formatter (always prints to stdout)
        _ = output_path

        # Format each diagnostic
        for diag in results.diagnostics:
            level = diag.level.value
            loc = diag.location
            code = f" [{diag.error_code}]" if diag.error_code else ""
            col = f":{loc.column}" if loc.column else ""
            print(f"{loc.file}:{loc.line}{col}: {level}: {diag.message}{code}")
            for note in diag.notes:
                print(f"  note: {note}")

        # Print summary
        print(results.format_summary())
