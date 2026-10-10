# 3. A workflow refreshes pixi.lock on pull requests

Date: 2026-10-10
Status: accepted

## Context

CI installs the environment with `setup-pixi`, which runs `pixi install
--locked` whenever `pixi.lock` exists, so a pull request that changes
`pyproject.toml` without the lockfile to match fails every job before any
test. Locally, every `just` recipe that runs a task updates the lockfile, but
only where pixi can reach what it resolves with: besides the package channels,
that is `conda-mapping.prefix.dev`, which maps conda packages to their PyPI
names. A cloud session whose network policy denied that host could change the
channels in `pyproject.toml` for the final Python 3.15, but not lock them.

Two things GitHub does decide how a workflow can supply the lockfile:

- A `pull_request` run uses the workflows of the pull request's merge commit,
  so a workflow added by a pull request already runs on that pull request.
- A push made with the workflow's `GITHUB_TOKEN` starts no `pull_request` or
  `push` run of its own, so CI does not run on a commit a workflow makes that
  way. `workflow_dispatch` is the exception. GitHub is rolling out
  `pull_request` runs that wait for a maintainer's approval after such a push,
  and this repository has them: they appeared on the first commit Lock made.

## Decision

**The Lock workflow runs `pixi lock` on a pull request that changes
`pyproject.toml` or `pixi.lock`, and commits the lockfile to its branch if it
changed.** It commits as `github-actions[bot]`, with `GITHUB_TOKEN`, so the
repository needs no secret.

**It then dispatches CI on the branch.** CI accepts `workflow_dispatch` for
this. A dispatched run tests the branch's head, where a `pull_request` run
tests its merge with the base branch; the two differ only when the base has
moved on.

**Pull requests from forks are skipped.** Their token is read-only. CI's locked
install tells their authors that the lockfile is stale, and any `just` recipe
updates it for them to commit.

**Rejected:**

- **A personal access token or a GitHub App's token**, whose push would start
  CI as any other does. Either is a secret to create, store and rotate, and the
  repository has none.
- **Relying on the approval GitHub asks for after the bot's push.** Every
  refresh would wait for a maintainer to approve the runs, and a repository
  the rollout has not reached would get no CI on the new commit at all.
- **Uploading the lockfile as an artifact** for someone to commit. It leaves
  the step this workflow exists to remove.

## Consequences

- A pull request whose lockfile was stale shows CI failing on the commit
  before the bot's, and passing, or not, on the bot's.
- The bot's commit also shows CI and Lock runs awaiting approval. The
  dispatched run has already tested the commit, so they can be left alone;
  approving them runs CI again and finds the lockfile current.
- If the branch moves on while Lock runs, its push is refused, and the new
  push starts Lock again.
- The lockfile is written by the latest pixi, as CI installs it, so a pixi
  release that changes the lockfile's format rewrites it on the next pull
  request that changes `pyproject.toml`.
