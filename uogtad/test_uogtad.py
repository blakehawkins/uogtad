from uogtad import Either, Fallible, Maybe

from typing import cast, Literal

def test_either():
    mainline = Either.new(1)
    mainline = mainline.map(lambda z: z + 1)
    
    assert mainline.narrow().narrow() == 2

    circuitous = mainline.flat_map(lambda z: Either.new(z + 1) if z == 2 else Either.right("???"))
    
    assert circuitous.narrow().narrow() == 3

def test_doc_example():
    input = lambda _: "🛸"  # Override input for pytest

    def raises():
        raise RuntimeError("tada")

    tada: str | None = Fallible(raises).as_result().swap().map(lambda exc: cast(str, exc.args[0])).narrow().narrow()
    assert tada == "tada"

    def categorise(num: int) -> Either[Literal['A'], Literal['B']]:
        if num == 0:
            return Either.new('A')  # Either is left-biased, like Result[T, E].
        return Either.right('B')

    just_a_lits: list[Literal['A']] = [
        cast(Literal['A'], y.narrow().narrow()) for y in [
            categorise(x) for x in [0, 1, 0, 2, 0, 3]
        ] if y.is_left()
    ]
    assert just_a_lits == ["A", "A", "A"]

    signal = None
    inp = input("🐊")
    possibly: Maybe[str] = Maybe(inp == "🛸").flat_map(lambda is_spaceship: Maybe("🐊") if is_spaceship else Maybe(None))
    def signal_change(croc: str) -> None:
        nonlocal signal
        signal = f"💻 You got the croc! {croc}"
    possibly.if_present(signal_change)
    print(signal)
    assert signal is not None
