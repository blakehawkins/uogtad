from collections.abc import Callable
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError
from pickle import HIGHEST_PROTOCOL, dumps, loads
from typing import assert_type

import pytest

from uogtad import Empty, Maybe, Some


@pytest.mark.parametrize("reconstruct", [copy, deepcopy])
@pytest.mark.parametrize("value", [None, False, 0, "", [], {"items": [1]}])
def test_some_copy_preserves_value_and_variant(
    value: object, reconstruct: Callable[[Some[object]], Some[object]]
) -> None:
    some = Some(value)
    restored = reconstruct(some)

    assert type(restored) is Some
    assert restored == some
    assert restored is not some
    assert restored.is_present()


@pytest.mark.parametrize("protocol", range(HIGHEST_PROTOCOL + 1))
@pytest.mark.parametrize("maybe", [Some(None), Some(False), Some(0), Some(""), Some([]), Some({"items": [1]}), Empty()])
def test_maybe_pickle_preserves_value_and_variant(maybe: Maybe[object], protocol: int) -> None:
    restored: Maybe[object] = loads(dumps(maybe, protocol=protocol))

    assert type(restored) is type(maybe)
    assert restored == maybe
    assert restored.is_present() == maybe.is_present()


def test_some_copy_shares_payload_and_deepcopy_isolates_it() -> None:
    shared = [1]
    some = Some([shared, shared])
    shallow = copy(some)
    deep = deepcopy(some)

    assert shallow.value is some.value
    assert deep.value is not some.value
    assert deep.value[0] is deep.value[1]
    assert deep.value[0] is not shared
    deep.value[0].append(2)
    assert shared == [1]


def test_some_deepcopy_preserves_cycles() -> None:
    payload: list[Some[object]] = []
    some = Some(payload)
    payload.append(some)

    restored = deepcopy(some)

    assert restored is not some
    assert restored.value is not payload
    assert restored.value[0] is restored


@pytest.mark.parametrize("protocol", range(HIGHEST_PROTOCOL + 1))
def test_some_pickle_preserves_cycles(protocol: int) -> None:
    payload: list[Some[object]] = []
    some = Some(payload)
    payload.append(some)

    restored: Some[list[Some[object]]] = loads(dumps(some, protocol=protocol))

    assert restored.value[0] is restored


def test_empty_supports_copy_and_deepcopy() -> None:
    empty = Empty()
    for restored in (copy(empty), deepcopy(empty)):
        assert type(restored) is Empty
        assert restored == empty
        assert not restored.is_present()


def test_reconstructed_some_remains_frozen_and_typed() -> None:
    some = Some(1)
    assert_type(Some(value=1), Some[int])
    assert_type(Some(None), Some[None])
    assert_type(copy(some), Some[int])
    assert_type(deepcopy(some), Some[int])
    unpickled: Some[int] = loads(dumps(some))

    for restored in (copy(some), deepcopy(some), unpickled):
        with pytest.raises(FrozenInstanceError):
            restored.value = 2  # type: ignore[misc]


def test_some_constructor_still_requires_a_value() -> None:
    with pytest.raises(TypeError):
        Some()  # type: ignore[call-arg]
