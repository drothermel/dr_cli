"""Error that generates notes for mypy testing."""


def process_items(items: list[str]) -> None:
    """Process a list of strings."""
    for item in items:
        print(item.upper())


# Type error with note about expected type
process_items([1, 2, 3])
