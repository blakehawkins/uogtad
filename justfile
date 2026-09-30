# The entry point for every command a developer runs here.
#
# Each recipe wraps the pixi task of the same name in pyproject.toml, except
# validate, which runs the others. `just --list` answers "what can I run", and
# pixi still provides the environment, installing whatever it lacks the first
# time a task needs it. `just` is installed on the system beside pixi, not as a
# dependency of the project.

# Show the available commands
default:
    @just --list --unsorted

# Everything CI checks in the code: the tests, then both type checkers
validate: test typecheck

# Run the tests; arguments go to pytest, as in `just test -k validation`
test *arguments:
    pixi run test {{arguments}}

# Type-check with mypy (strict) and pyright
typecheck:
    pixi run typecheck

# Build the source and wheel distributions, and check them with twine
package:
    pixi run package
