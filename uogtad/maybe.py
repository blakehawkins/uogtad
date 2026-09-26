"""The optional-value :class:`Maybe` container."""

from dataclasses import dataclass
from typing import Callable, Never, cast

from uogtad.either import Either, Left, Right


class Maybe[T]:
    """A value represented by either :class:`Some` or :class:`Empty`.

    ``Maybe(value)`` is retained as a convenient spelling for ``Some(value)``;
    unlike the previous implementation, ``None`` is a valid present value.
    """

    def __new__[V](cls, value: V) -> "Maybe[V]":
        if cls is Maybe:
            return cast(Maybe[V], Some(value))
        return cast(Maybe[V], super().__new__(cls))

    @classmethod
    def empty[V](cls) -> "Maybe[V]":  # pyright: ignore[reportInvalidTypeVarUse]
        return cast(Maybe[V], Empty())

    def is_present(self) -> bool:
        return isinstance(self, Some)

    def context(self, context: str) -> Either[T, RuntimeError]:
        if isinstance(self, Some):
            return cast(Either[T, RuntimeError], Left(self.value))
        return cast(Either[T, RuntimeError], Right(RuntimeError(context)))

    def or_else[V](self, instead: V) -> T | V:
        if isinstance(self, Some):
            return cast(Some[T], self).value
        return instead

    def or_else_get[V](self, instead_provider: Callable[[], V]) -> T | V:
        if isinstance(self, Some):
            return cast(Some[T], self).value
        return instead_provider()

    def if_present(self, with_: Callable[[T], object]) -> None:
        if isinstance(self, Some):
            with_(self.value)

    def filter(self, clause: Callable[[T], bool]) -> "Maybe[T]":
        if isinstance(self, Some) and clause(self.value):
            return self
        return cast(Maybe[T], Empty())

    def map[V](self, function: Callable[[T], V]) -> "Maybe[V]":
        if isinstance(self, Some):
            return Some(function(self.value))
        return cast(Maybe[V], Empty())

    def narrow(self) -> T | None:
        if isinstance(self, Some):
            return cast(Some[T], self).value
        return None

    def flat_map[V](self, function: Callable[[T], "Maybe[V]"]) -> "Maybe[V]":
        if isinstance(self, Some):
            return function(self.value)
        return cast(Maybe[V], Empty())


@dataclass(frozen=True)
class Some[L](Maybe[L]):
    """The present case of :class:`Maybe`."""

    value: L


@dataclass(frozen=True)
class Empty(Maybe[Never]):
    """The absent case of :class:`Maybe`."""

    def __new__(cls) -> "Empty":
        return object.__new__(cls)


__all__ = ["Maybe", "Some", "Empty"]
