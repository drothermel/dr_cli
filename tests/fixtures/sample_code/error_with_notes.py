"""Error that generates notes for mypy testing."""

from typing import List


def process_items(items: List[str]) -> None:
    """Process a list of strings."""
    for item in items:
        print(item.upper())


# Type error with note about expected type
process_items([1, 2, 3])