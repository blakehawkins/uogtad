# Contributor instructions

- Do not use `setattr`, including `object.__setattr__`, in this repository.
- Keep all imports at module scope. Inline imports are forbidden.

## Recording release changes

Release Please uses Conventional Commits as this repository's change records.
Every pull request title must use Conventional Commit syntax. Because pull
requests are squash-merged, the pull request title becomes the commit that
Release Please reads; a non-conventional title can prevent a release from being
created even when the pull request contains release-related changes.

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

## Design records

Decisions about the library's design are recorded in `adrs/`, one numbered
file each. Read the ones that cover an API before changing it, and add a
record when you make a decision someone would otherwise have to rediscover.

## Python 3.15 development environment

This project uses Python 3.15 syntax. Do not compile CPython or install a
separate interpreter manually. Pixi obtains the appropriate Python build from
the `conda-forge/label/python_rc` channel configured in `pyproject.toml`.

- Run every command through `just`, and `just validate` before pushing.
  `just --list` shows the rest. Pixi installs the environment, uogtad itself
  included, the first time a task needs it: there is no install step. Each
  recipe wraps the pixi task of the same name in `pyproject.toml`, and CI runs
  those tasks, so when you add a command, add both the task and its recipe.
  Never ask a developer to type `pixi run python -m ...`.
- If Pixi or just is unavailable, install its prebuilt executable from the
  official `prefix-dev/pixi` or `casey/just` GitHub releases; do not build
  Pixi, just or Python from source.
