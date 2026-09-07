---
description: Run the repo's verification loop on the current change and report real output - stage 4A of the SDLC loop.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(touch:*), Bash(rm:*), Bash(ls:*)
---

# Stage 4A — Every session checks its own work

Never hand a change to a human without having checked it yourself. This command runs the loop and reports literal output, not an assessment.

`$ARGUMENTS` may be `--lock-tests` / `--unlock-tests` (see step 5) or empty.

## Workflow

### 1. Find the verification command

In order:

1. `CLAUDE.md` — the build/test/lint commands and their healthy output (put there by `/sdlc:init`)
2. `Makefile`, `package.json` scripts, `Package.swift`, project scheme
3. Ask the user, then offer to write the answer into `CLAUDE.md` so this stage never has to ask again

### 2. Establish what "done" means

Read `sdlc/plan/<slug>.md` if one matches the current branch or change, and take the done-condition from its Tests section. Otherwise ask for a quantifiable target: which tests pass, what the build must produce, what the UI must show.

### 3. Run everything

Run build, tests, and lint — all of them, before reporting anything. Paste the real output, trimmed but not paraphrased. If a command fails, that is the result; report it as a failure with the output rather than describing what you would fix.

For UI changes, capture evidence: a screenshot, a rendered preview, or a driven run of the app. Iterate two or three rounds against the expected appearance before showing it to the user.

### 4. Delegate the behavioural pass

For anything beyond a unit-test-shaped change, launch the `verifier` subagent bundled with this skill. It runs the app, exercises the changed behaviour and the flows next to it, and reports what worked without fixing anything. Its findings go to the user as-is.

### 5. Test-file lock (bug fixes)

For a bug fix the order is: write the failing test first, commit it, then fix the code without touching the test.

- `--lock-tests` creates `sdlc/.lock-tests`. While that file exists, this skill's `PreToolUse` hook blocks edits to test files, so the fix cannot be made to pass by weakening the check.
- `--unlock-tests` removes it. Always remove the lock once the fix is verified, and tell the user it is off.

The hook does nothing when the marker file is absent — it never interferes with ordinary test writing.

### 6. Report

State plainly: what ran, what passed, what failed, what is unverified and why. If anything is unverified, say so instead of implying full coverage.
