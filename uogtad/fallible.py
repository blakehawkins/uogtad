"""The exception-capturing :class:`Fallible` container."""

from typing import Callable, cast

from uogtad._typing import narrowed
from uogtad.either import Either, Left, Right
from uogtad.maybe import Maybe


class Fallible[F]:
    """The successful return value or ordinary exception from a computation."""

    def __init__(self, computation: Callable[[], F]) -> None:
        try:
            self._result: Either[F, Exception] = narrowed(Left(computation()))
        except Exception as error:
            self._result = narrowed(Right(error))

    @classmethod
    def _from_result[V](cls, result: Either[V, Exception]) -> Fallible[V]:
        instance = cast(Fallible[V], cls.__new__(cls))
        instance._result = result
        return instance

    def as_result(self) -> Either[F, Exception]:
        return self._result

    def is_success(self) -> bool:
        return self._result.is_left()

    def is_exception(self) -> bool:
        return self._result.is_right()

    def maybe_success(self) -> Left[F] | None:
        """Return the concrete successful result, or ``None`` on failure."""
        return self._result.maybe_left()

    def maybe_exception(self) -> Right[Exception] | None:
        """Return the concrete failed result, or ``None`` on success."""
        return self._result.maybe_right()

    def map[V](self, function: Callable[[F], V]) -> Fallible[V]:
        match self._result:
            case Left(value):
                return Fallible(lambda: function(value))
            case Right(error):
                return Fallible._from_result(Right(error))
            case _:
                raise TypeError("unknown Either variant")

    def flat_map[V](self, function: Callable[[F], Fallible[V]]) -> Fallible[V]:
        match self._result:
            case Left(value):
                try:
                    return function(value)
                except Exception as error:
                    return Fallible._from_result(Right(error))
            case Right(error):
                return Fallible._from_result(Right(error))
            case _:
                raise TypeError("unknown Either variant")

    def narrow(self) -> Maybe[F]:
        return self._result.narrow()

    def or_else[V](self, recovery: Callable[[Exception], V]) -> F | V:
        return self._result.or_else(recovery)


__all__ = ["Fallible"]
