## Summary

<!-- What changes, and why. The title becomes the squash-merge commit, so it
uses Conventional Commit syntax: see AGENTS.md. -->

## Ready to merge?

<!-- Answer after each question, from the whole diff against the base branch,
with the evidence: what you ran, what it reported, and what you could not
check. -->

- **Consistent:** do the code, comments, docs and ADRs agree with each other
  and follow AGENTS.md?
- **Coherent:** does every change serve the summary, and is each drive-by
  change named?
- **Complete:** is anything left half-done, such as docs, ADRs, `pixi.lock` or
  a follow-up?
- **Maintainable:** is each decision someone would otherwise have to
  rediscover recorded in `adrs/`?
- **Readable:** can a reviewer follow the change from the diff and its
  comments alone?
- **Well-tested:** which tests and checks cover it, did `just validate` and CI
  pass, and what is untested?
- **Safe to merge:** what could go wrong once it is merged, and what is
  unverified?
