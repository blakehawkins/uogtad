from typing import TypeVar, Generic, Callable

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')
class Either(Generic[T, U]):
    """A class that holds either a T or a U. In contrast to a python Union type, this is a concrete wrapper."""
    _left: T | None
    _right: U | None

    def __init__(self, left: T, right: U):
        self._left = left
        self._right = right

    @classmethod
    def new(cls, t: T) -> 'Either':
        """Either is left-biased."""
        return cls(t, None)

    @classmethod
    def right(cls, u: U) -> 'Either':
        return cls(None, u)

    def context(self, context: str) -> 'Either':
        """If this is a right, returns this right wrapped in a RuntimeError with the provided context."""
        if self._left:
            return self

        return Either.right(RuntimeError(context, self._right))

    def is_left(self) -> bool:
        return self._left is not None

    def is_right(self) -> bool:
        return self._right is not None

    def swap(self) -> 'Either[U, T]':
        return Either.new(self._right) if self._right else Either.right(self._left)

    def or_else(self, otherwise: Callable[[U], T]) -> T:
        if self._left:
            return self._left
            
        assert self._right is not None
        return otherwise(self._right)

    def map(self, callable: Callable[[T], V]) -> 'Either[V, U]':
        if self._left:
            return Either.new(callable(self._left))
        
        return Either.right(self._right)

    def flat_map(self, callable: Callable[[T], 'Either[V, U]']) -> 'Either[V, U]':
        if self._left:
            return callable(self._left)

        return Either.right(self._right)

    def map_right(self, callable: Callable[[U], V]) -> 'Either[T, V]':
        if self._right:
            return Either.right(callable(self._right))

        return Either.new(self._left)

    def flat_map_right(self, callable: Callable[[U], 'Either[T, V]']) -> 'Either[T, V]':
        if self._right:
            return callable(self._right)

        return Either.new(self._left)

    def narrow(self) -> 'Maybe[T]':
        if self._left:
            return Maybe(self._left)

        return Maybe.empty()

    def if_left(self, then_: Callable[[T], None]) -> None:
        if self._left:
            then_(self._left)

    def if_right(self, then_: Callable[[U], None]) -> None:
        if self._right:
            then_(self._right)


F = TypeVar('F')
G = TypeVar('G')
class Fallible(Generic[F]):
    """Represents the (un)successful computation of a Callable as either its return value or an Exception."""

    def __init__(self, computation: Callable[[], F]):
        self._ret: F | None = None
        self._exc: BaseException | None = None

        try:
            self._ret = computation()
        except BaseException as e:
            self._exc = e

    def as_result(self) -> Either[F, BaseException]:
        if self._exc:
            return Either.right(self._exc)

        return Either.new(self._ret)

    def is_success(self) -> bool:
        return self._ret is not None

    def is_exception(self) -> bool:
        return self._exc is not None

    def if_success(self, then_: Callable[[F], None]) -> None:
        return self._ret and then_(self._ret)
    
    def if_exception(self, then_: Callable[[BaseException], None]) -> None:
        return self._exc and then_(self._exc)

    def map(self, callable: Callable[[F], G]) -> 'Fallible[G]':
        if self._ret:
            val = callable(self._ret)
            return Fallible(lambda: val)

        def raiser():
            assert self._exc
            raise self._exc
        return Fallible(raiser)

    def flat_map(self, callable: Callable[[F], 'Fallible[G]']) -> 'Fallible[G]':
        if self._ret:
            def inner():
                assert self._ret
                return callable(self._ret)
            return inner()
        
        def raiser():
            assert self._exc
            raise self._exc
        return Fallible(raiser)

    def narrow(self) -> 'Maybe[F]':
        return Maybe(self._ret)

    def or_else(self, recovery: Callable[[BaseException], F]) -> F:
        if self._ret:
            return self._ret
            
        assert self._exc
        return recovery(self._exc)


A = TypeVar('A')
B = TypeVar('B')
class Maybe(Generic[A]):
    """
    A type-safe wrapper for a value or its absense.
    This is not the same thing as a `Union[T, None]` but rather a monad for computations over that form.
    Confusingly, in some languages this is called Optional -- but in python, Optional is an alias for Union[T, None].
    """
    _val: A | None
    _present: bool
    
    def __init__(self, val: A | None) -> None:
        self._val = val
        self._present = val is not None

    @classmethod
    def empty(cls):
        return cls(None)

    def context(self, context: str) -> Either[A, BaseException]:
        """Adds context to this, yielding an Either[T, E] with an Exception built from `context` if this is Empty."""
        if self._present:
            return Either.new(self._val)
        
        return Either.right(RuntimeError(context))

    def is_present(self) -> bool:
        return self._present

    def or_else(self, instead: A) -> A:
        return self._val or instead

    def or_else_get(self, instead_provider: Callable[[], A]) -> A:
        return self._val or instead_provider()

    def if_present(self, with_: Callable[[A], None]) -> None:
        if self._present:
            assert self._val is not None
            with_(self._val)

    def filter(self, clause: Callable[[A], bool]) -> 'Maybe[A]':
        if self._present:
            assert self._val
            if clause(self._val):
                return self
        
        return Maybe.empty()

    def map(self, callable: Callable[[A], B]) -> 'Maybe[B]':
        if self._present and self._val:
            return Maybe(callable(self._val))
        
        return Maybe(None)

    def narrow(self) -> A | None:
        if self._present:
            return self._val

        return None

    def flat_map(self, callable: Callable[[A], 'Maybe[B]']) -> 'Maybe[B]':
        if self._present and self._val:
            return callable(self._val)
        
        return Maybe(None)
