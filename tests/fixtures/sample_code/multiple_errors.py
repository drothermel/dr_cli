"""Multiple type errors in one file."""


def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}"


# Name error - undefined variable
x = undefined_variable  # noqa: F821

# Type error - wrong type assignment
y: int = "not a number"

# Argument type error
z = greet(123)
