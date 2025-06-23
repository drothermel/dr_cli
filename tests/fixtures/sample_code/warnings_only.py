"""File with only warnings, no errors."""

from typing import cast

# Unused import - generates warning with --warn-unused-ignores

# This generates a warning about redundant cast
x = cast("int", 5)

# Unused variable
y = 10
