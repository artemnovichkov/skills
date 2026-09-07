---
description: Produce sdlc/plan/<slug>.md from an accepted spec - nothing gets implemented without an accepted plan.
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(ls:*)
---

# Stage 3 — Nothing implemented without an accepted plan

Design review happens before code generation, not in the PR. The plan must be reviewable on its own: someone who has not read the diff should be able to say "yes, that is the right change" or "no, that breaks X".

`$ARGUMENTS` is the slug. If empty, list `sdlc/spec/` and ask.

## Workflow

### 1. Prefer plan mode

If the session is **not** in plan mode, tell the user: press `shift+tab` to enter plan mode, then re-run this command. Plan mode makes the read-only constraint real rather than a promise. If they would rather not, continue in read-only discipline: read and search only, no edits.

### 2. Load intent and spec

Read `sdlc/intent/<slug>.md` and `sdlc/spec/<slug>.md`, plus `CLAUDE.md`. Then read the actual files the spec names — the plan is only worth something if it names real files and real functions.

Look for existing utilities, helpers, and patterns to reuse. A plan that proposes new code where the repo already has an implementation is a bad plan.

### 3. Draft the plan

Use `${CLAUDE_PLUGIN_ROOT}/templates/plan.md`:

- Files to change, each with what changes and why — real paths, not categories.
- Work order, with the dependency between steps made explicit.
- Tests required: which existing tests cover this, which new ones are needed, what each asserts.
- What could break: neighbouring behaviour, callers, migrations, platform edges.
- Rollback: how this gets undone if it goes wrong.

### 4. Interrogate it

Before showing it as finished, answer these in the plan itself:

- What breaks if this ships as written?
- What is the riskiest step, and what makes it less risky?
- What is the alternative approach, and why is this one better?

Then hand it to the user and iterate until they accept it.

### 5. Persist and commit

Write the accepted plan to `sdlc/plan/<slug>.md` with `Status: accepted`. If the session used plan mode, copy the approved plan file's content into it rather than rewriting from memory.

```
git add sdlc/plan/<slug>.md && git commit -m "plan: <title>"
```

### 6. During implementation

While implementing, if the work departs from the plan — a step turns out impossible, a file was missed, an approach changes — **update `sdlc/plan/<slug>.md` in the same commit as the code**. Do not let the plan drift; a stale plan is worse than none.

When implementation is done, run `/sdlc:verify` before reporting anything as complete.
