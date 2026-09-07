# Review Policy

How every change in this repo gets reviewed. Same passes, every time.

## Passes

### 1. Bugs and logic

Logic errors, regressions, unhandled edge cases, wrong error handling,
concurrency and lifecycle mistakes, resource leaks.

### 2. Security

Injection, authentication and authorisation gaps, secrets in code or logs,
PII in logs or error messages, unsafe deserialisation, unvalidated input
crossing a trust boundary.

### 3. Compliance

Does the diff implement the accepted spec? Does it match the accepted plan?
Does it follow the conventions in `CLAUDE.md`? Name divergences explicitly -
a divergence is not automatically wrong, but it must be visible.

## Important vs Nit

**Important** — anything that changes behaviour, risks data, breaks a contract,
or contradicts the spec or plan.

**Nit** — naming, formatting, comment wording, ordering, personal preference.

Cap: at most 5 nits per review. If there are more, the pattern belongs in a
linter or in `CLAUDE.md`, not in review comments.

## Excluded from review

- Generated code: <paths>
- Vendored dependencies: <paths>
- Anything CI already enforces: <formatter, linter, type checker>

## Boundary

The reviewer does not approve or merge. Findings go to a human, who decides.

## Feedback loop

A finding that repeats a correction already made once goes into `CLAUDE.md`
instead of being fixed by hand again.
