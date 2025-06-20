"""File with only warnings, no errors."""

from typing import Any, cast

# Unused import - generates warning with --warn-unused-ignores
import os  # type: ignore[unused-import]

# This generates a warning about redundant cast
x = cast(int, 5)

# Unused variable
y = 10