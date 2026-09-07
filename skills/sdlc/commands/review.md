---
description: Define review policy in REVIEW.md and run it against the current change - stage 5 of the SDLC loop.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(gh pr:*)
---

# Stage 5 — Review the same way every time

Every change gets the same passes, so human attention can go to intent and risk instead of to naming and formatting.

## Workflow

### 1. Ensure a review policy exists

If `REVIEW.md` is absent, draft it from `${CLAUDE_PLUGIN_ROOT}/templates/REVIEW.md`, adapted to this repo:

- **Passes**: bugs and logic errors; security and vulnerabilities; compliance with the spec, the plan, and the repo's stated principles.
- **Important vs Nit**: define the line explicitly. Style and naming are nits. Cap the number of nits reported.
- **Exclusions**: generated paths, vendored code, and anything CI already enforces — commenting on those wastes the review.

Show it to the user for correction and offer the commit. `REVIEW.md` is policy: it is worth arguing over once so it does not have to be argued in every PR.

### 2. Run the review

Reuse the existing reviewer rather than writing another one:

- If the `code-review` plugin is installed, run `/code-review` and pass `REVIEW.md` as the policy the review must apply, along with `sdlc/spec/<slug>.md` and `sdlc/plan/<slug>.md` for the compliance pass.
- Otherwise, review the diff yourself against each `REVIEW.md` pass in turn, one pass at a time. Report findings ranked by severity, and drop anything that is only style.

The compliance pass is the one a generic reviewer cannot do: does the diff actually implement the accepted spec, and does it match the accepted plan? Name the divergences.

### 3. Close the loop

- Any finding that is a repeat of an earlier correction goes into `CLAUDE.md` — that is what stops it recurring.
- If the diff departs from the plan, update `sdlc/plan/<slug>.md`.
- For a GitHub PR, the user can tag `@claude` on review comments to have them addressed on the branch.

### 4. Boundary

You do not approve your own work. Present findings and let the user decide what merges. If asked to merge, say plainly that the merge decision is theirs and wait for an explicit go-ahead.
