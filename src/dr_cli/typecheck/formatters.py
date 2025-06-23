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
