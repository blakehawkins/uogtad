"""Small, typed containers for functional-style control flow."""

from uogtad.either import Either, Left, Right
from uogtad.fallible import Fallible
from uogtad.maybe import Empty, Maybe, Some

__all__ = ["Either", "Left", "Right", "Maybe", "Some", "Empty", "Fallible"]
