---
description: Capture an idea, feature, or bug as sdlc/intent/<slug>.md - the proto-spec that starts the loop.
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(ls:*)
---

# Stage 1 — Capture as intent

Turn a rough idea into a committed, machine-readable intent. This is the cheapest stage to be wrong in: the goal is a document worth arguing with, not a finished spec.

`$ARGUMENTS` is the raw idea. If empty, ask the user what they want to build or fix.

## Workflow

### 1. Interview, do not transcribe

Ask about whatever the idea does not already answer — one round, not an interrogation:

- What is broken or missing today, and who feels it?
- What does "done" look like from outside the code?
- Which parts of the system does this touch? (search the repo and propose an answer instead of asking blind)
- What is explicitly out of scope?
- What constraints are fixed — deadline, platform, dependency, compatibility?

If the repo has `CLAUDE.md`, read it first so questions do not re-ask what the repo already documents.

### 2. Draft the artifact

Use `${CLAUDE_PLUGIN_ROOT}/templates/intent.md`. Write `sdlc/intent/<slug>.md` where `<slug>` is kebab-case, derived from the title, max 5 words. Check for a slug collision in `sdlc/intent/` first.

Rules for the draft:

- Problem stated as an observed fact, not as a solution in disguise.
- Outcome measurable by someone who cannot read the diff.
- Open questions listed honestly — an intent with zero open questions is usually a lie, and the list is what the spec stage resolves.
- No implementation detail. If you catch yourself naming a class or a file, it belongs in the spec or plan.
- `Status: draft`.

### 3. Hand back for correction

Show the draft and ask for corrections. Iterate until the user accepts it, then flip `Status:` to `accepted`.

### 4. Offer the commit

Print the exact command:

```
git add sdlc/intent/<slug>.md && git commit -m "intent: <title>"
```

Do not run it without the user saying so. Then tell them the accepted intent unlocks `/sdlc:spec <slug>`.
