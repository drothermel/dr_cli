"""File that generates error with notes about overload variants."""

from typing import overload


@overload
def process(x: int) -> str: ...


@overload
def process(x: str) -> int: ...


def process(x):  # noqa: D103
    if isinstance(x, int):
        return str(x)
    else:
        return int(x)


# This will generate an error with notes about possible overload variants
result = process([1, 2, 3])
