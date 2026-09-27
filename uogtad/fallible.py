"""The exception-capturing :class:`Fallible` container."""

from typing import Callable

from uogtad.either import Either, Left, Right
from uogtad.maybe import Maybe


class Fallible[F, E: Exception = Exception]:
    """The return value or a selected exception from a computation.

    By default, all ordinary exceptions are captured.  Pass an exception class
    or tuple of exception classes to let unrelated exceptions propagate.
    """

    def __init__(
        self,
        computation: Callable[[], F],
        exceptions: type[E] | tuple[type[E], ...] = Exception,
    ) -> None:
        self._exceptions = exceptions
        try:
            self._result: Either[F, E] = Either[F, E].new(computation())
        except exceptions as error:
            self._result = Either[F, E].right(error)

    @classmethod
    def _from_result(
        cls,
        result: Either[F, E],
        exceptions: type[E] | tuple[type[E], ...],
    ) -> Fallible[F, E]:
        instance = cls.__new__(cls)
        instance._result = result
        instance._exceptions = exceptions
        return instance

    def as_result(self) -> Either[F, E]:
        return self._result

    def is_success(self) -> bool:
        return self._result.is_left()

    def is_exception(self) -> bool:
        return self._result.is_right()

    def maybe_success(self) -> Left[F, E] | None:
        """Return the concrete successful result, or ``None`` on failure."""
        return self._result.maybe_left()

    def maybe_exception(self) -> Right[E, F] | None:
        """Return the concrete failed result, or ``None`` on success."""
        return self._result.maybe_right()

    def map[V](self, function: Callable[[F], V]) -> Fallible[V, E]:
        match self._result:
            case Left(value):
                return Fallible[V, E](lambda: function(value), self._exceptions)
            case Right(error):
                return Fallible[V, E]._from_result(Right(error), self._exceptions)
            case _:
                raise TypeError("unknown Either variant")

    def flat_map[V](
        self, function: Callable[[F], Fallible[V, E]]
    ) -> Fallible[V, E]:
        match self._result:
            case Left(value):
                try:
                    return function(value)
                except self._exceptions as error:
                    return Fallible[V, E]._from_result(Right(error), self._exceptions)
            case Right(error):
                return Fallible[V, E]._from_result(Right(error), self._exceptions)
            case _:
                raise TypeError("unknown Either variant")

    def narrow(self) -> Maybe[F]:
        return self._result.narrow()

    def or_else[V](self, recovery: Callable[[E], V]) -> F | V:
        return self._result.or_else(recovery)


__all__ = ["Fallible"]
