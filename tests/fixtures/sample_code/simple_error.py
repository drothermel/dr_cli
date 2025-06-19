"""Simple type error for mypy testing."""


def add_numbers(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


# Type error: passing str instead of int
result = add_numbers("5", 10)