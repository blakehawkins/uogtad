"""Internal typing helpers."""

from typing import cast


def narrowed[T](value: object) -> T:  # type: ignore[type-var]
    """Return a pattern-matched value with its generic type restored."""
    return cast(T, value)
