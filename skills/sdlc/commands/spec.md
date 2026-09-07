---
description: Turn an accepted intent into sdlc/spec/<slug>.md - requirements and design in one pass, with concerns flagged.
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(ls:*)
---

# Stage 2 — Requirements and design collapse into one session

Requirements analysis and design happen in the same session. The point is not speed for its own sake: policy gets applied while the spec is written instead of being discovered in review later.

`$ARGUMENTS` is the slug. If empty, list `sdlc/intent/` and ask which intent to work from.

## Workflow

### 1. Load the constraints

- Read `sdlc/intent/<slug>.md`. If its `Status:` is not `accepted`, say so and ask whether to proceed anyway.
- Read `CLAUDE.md` for repo conventions and architecture.
- Load whatever policy the repo carries: skills in `.claude/skills/`, `CONVENTIONS.md`, `ARCHITECTURE.md`, security or style docs. These are the constraints the spec must satisfy.
- Read the code the intent touches. A spec written without reading the affected files is guesswork.

### 2. Draft the spec

Use `${CLAUDE_PLUGIN_ROOT}/templates/spec.md` and write `sdlc/spec/<slug>.md`:

- Requirements as testable statements, each traceable to something in the intent.
- Design: the approach, the data/state changes, the interfaces that move, what stays untouched.
- Alternatives considered, with the reason each was dropped — one line each.
- **Concerns**, explicitly flagged: anything where the design collides with a repo convention, a security or privacy surface, a migration, a performance cliff, or an open question the intent left unresolved. Flag it; do not resolve it silently.
- Answer every open question from the intent, or restate it as a concern.
- `Status: draft`.

### 3. Resolve concerns with the user

Walk the concerns one at a time. Each ends as: resolved (with the decision recorded in the spec), accepted risk (recorded as such), or deferred to a follow-up intent.

### 4. Accept and commit

Flip to `Status: accepted` once the user agrees, then print:

```
git add sdlc/spec/<slug>.md && git commit -m "spec: <title>"
```

Next step: `/sdlc:plan <slug>`.
