# Contributor instructions

- Do not use `setattr`, including `object.__setattr__`, in this repository.
- Keep all imports at module scope. Inline imports are forbidden.

## Recording release changes

Release Please uses Conventional Commits as this repository's change records.
Give every pull request a squash-merge title in the form `type: summary` (or
`type(scope): summary`) so the resulting commit can be included in the staged
release pull request:

- `fix:` records a patch release.
- `feat:` records a minor release.
- Add a `BREAKING CHANGE:` footer to record a major release.
- `docs:`, `test:`, `refactor:`, `build:`, `ci:`, and `chore:` do not trigger a
  release unless they include a `Release-As: x.y.z` footer.

Use the pull request body for a longer explanation when the summary alone is
not enough. Do not edit the version or `CHANGELOG.md` in feature pull requests;
the automated release pull request owns those files.

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
