# Contributor instructions

- Do not use `setattr`, including `object.__setattr__`, in this repository.
- Keep all imports at module scope. Inline imports are forbidden.

## Python 3.15 development environment

This project uses Python 3.15 syntax. Do not compile CPython or install a
separate interpreter manually. Pixi obtains the appropriate Python build from
the `conda-forge/label/python_rc` channel configured in `pyproject.toml`.

- Run commands in the environment with `pixi run`, for example
  `pixi run python -m pytest -q`.
- Install the project and its development dependencies with
  `pixi run python -m pip install -e ".[test,typecheck]"`.
- If Pixi itself is unavailable, install its prebuilt executable from the
  official `prefix-dev/pixi` GitHub releases; do not build Pixi or Python from
  source.
