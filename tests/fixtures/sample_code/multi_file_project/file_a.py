"""First file with type error."""


def calculate(x: int) -> int:
    """Double the input."""
    return x * 2


# Type error in file_a
result = calculate("string")
