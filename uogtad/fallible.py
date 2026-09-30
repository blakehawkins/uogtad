"""The exception-capturing :class:`Fallible` container."""

from typing import Callable, Generic, TypeVar, cast, overload

from uogtad.either import Either, Left, Right
from uogtad.maybe import Maybe
from uogtad.validation import Validation


# Covariant, and declared: with the class syntax, mypy would infer Fallible as
# invariant, since it cannot infer variance through flat_map's widened result,
# Fallible[V, E | G], while E has a bound. The result and the captured exception
# types are set once, as a Fallible is made, and never reassigned, which is what
# makes covariance sound.
F = TypeVar("F", covariant=True)
E = TypeVar("E", bound=Exception, default=Exception, covariant=True)


class Fallible(Generic[F, E]):
    """The return value or a selected exception from a computation.

    By default, all ordinary exceptions are captured.  Pass an exception class
    or tuple of exception classes to let unrelated exceptions propagate.
    """

    @overload
    def __init__(self, computation: Callable[[], F]) -> None: ...

    @overload
    def __init__(
        self,
        computation: Callable[[], F],
        exceptions: type[E] | tuple[type[E], ...],
    ) -> None: ...

    def __init__(
        self,
        computation: Callable[[], F],
        exceptions: type[E] | tuple[type[E], ...] = cast(type[E], Exception),
    ) -> None:
        self._exceptions = exceptions
        try:
            self._result: Either[F, E] = Either[F, E].new(computation())
        except exceptions as error:
            self._result = Either[F, E].right(error)

    @classmethod
    def _from_result[V, G: Exception](
        cls: type[Fallible[V, G]],
        result: Either[V, G],
        exceptions: type[G] | tuple[type[G], ...],
    ) -> Fallible[V, G]:
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

    def flat_map[V, G: Exception](
        self, function: Callable[[F], Fallible[V, G]]
    ) -> Fallible[V, E | G]:
        """Run a step that makes a fallible of its own, which may capture
        different exceptions: the result may hold either kind.

        An exception this fallible captures is captured from ``function``
        itself too. What later steps capture depends on which fallible the
        result is: the step's, if this one succeeded, or this one otherwise.
        """
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

    def as_validation(self) -> Validation[F, E]:
        """A validation of the result, or of the captured exception as its one error."""
        return self._result.as_validation()

    def narrow(self) -> Maybe[F]:
        return self._result.narrow()

    def or_else[V](self, recovery: Callable[[E], V]) -> F | V:
        return self._result.or_else(recovery)


__all__ = ["Fallible"]
