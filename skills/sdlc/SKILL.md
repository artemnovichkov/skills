---
name: sdlc
description: Run an artifact-driven software lifecycle where each stage commits a markdown artifact that triggers the next - intent.md, spec.md, plan.md, verified diff, reviewed PR, monitored production. Use when the user asks to capture an idea as intent, write a spec, plan before implementing, set up a verification loop, define review policy, add agent-config evals, or wire production alerts back into the loop.
---

# sdlc

Turns an idea into shipped, verified code through six stages. Each stage produces one markdown artifact in `sdlc/`, committed to git. The artifact is the handoff: no stage starts until the previous one's artifact exists and the user has accepted it.

Adapted from Anthropic's [AI-Native SDLC Playbook](https://claude.com/blog/the-ai-native-sdlc-playbook), trimmed for a solo developer. The org-scale layer (separation of duties, policy owners, leading/lagging metrics) lives in `references/governance.md` and is opt-in.

## When to Use

Activate when the user asks to:

- Capture an idea, feature, or bug as a written intent before building
- Turn an intent into a requirements/design spec
- Plan an implementation before writing code
- Set up a verification loop so changes check themselves before review
- Define review policy (`REVIEW.md`) or run policy-driven review
- Add regression evals for agent configuration (`CLAUDE.md`, skills, hooks)
- Wire production metrics back into the planning loop

Also activate when a repo already has an `sdlc/` directory and the user references an artifact in it.

## The Artifact Chain

```
sdlc/intent/<slug>.md   -> what problem, why now, constraints, open questions
sdlc/spec/<slug>.md     -> requirements + design, concerns flagged
sdlc/plan/<slug>.md     -> files to change, work order, tests required
<diff> + tests          -> verified before a human looks
PR + REVIEW.md passes   -> reviewed against the spec and plan
production signal       -> new sdlc/intent/<slug>.md, loop restarts
```

One `<slug>` runs through all three files. That slug is the audit trail — `git log sdlc/*/<slug>.md` shows the whole decision history for a change.

## Commands

| Command | Stage | Produces |
| --- | --- | --- |
| `/sdlc:init` | setup | `sdlc/` scaffold, `REVIEW.md`, `CLAUDE.md` sections |
| `/sdlc:intent` | 1. Plan | `sdlc/intent/<slug>.md` |
| `/sdlc:spec` | 2. Design | `sdlc/spec/<slug>.md` |
| `/sdlc:plan` | 3. Build | `sdlc/plan/<slug>.md` |
| `/sdlc:verify` | 4. Test | verification report, optional test-file lock |
| `/sdlc:evals` | 4. Test | `evals/` suite + CI workflow |
| `/sdlc:review` | 5. Deploy | `REVIEW.md`, then delegates to `/code-review` |
| `/sdlc:bands` | 6. Maintain | `sdlc/bands.yaml` + watcher script |

Stage details, measurement, and governance notes: `references/stages.md`.

## Core Rules

**Never skip an artifact.** If the user asks to implement something and no `sdlc/plan/<slug>.md` exists, say so and offer `/sdlc:plan` first. If they decline, proceed — but do not silently pretend a plan exists.

**Never write the artifact alone.** Each command drafts, then asks the user to correct. The user's acceptance is what triggers the next stage. Skipping their review turns the chain into theatre.

**Never auto-commit.** Write the file, show what changed, offer the exact `git add` + `git commit` command. The user runs it or tells you to.

**Plan must stay true.** If implementation departs from `sdlc/plan/<slug>.md`, update the plan in the same commit as the code. A stale plan is worse than no plan.

**Always verify before reporting done.** Run the repo's verification command (from `CLAUDE.md`) and paste real output. "Should work" is not a result. See `/sdlc:verify`.

**Second mistake goes in `CLAUDE.md`.** When the same correction is needed twice, write it into the repo's `CLAUDE.md` rather than fixing it again by hand.

## Conventions

- Artifacts live in `sdlc/` at repo root. Slug: kebab-case, derived from the intent title, max 5 words.
- Templates in `templates/` are starting points — strip sections that do not apply rather than filling them with filler.
- Every artifact opens with a `Status:` line (`draft` / `accepted` / `superseded by <slug>`).
- The test-file guard hook is **off** unless `sdlc/.lock-tests` exists. See `hooks/README` notes in `references/stages.md`.

## Requirements

- Git repository
- `CLAUDE.md` at repo root (`/sdlc:init` creates or extends it)
- For `/sdlc:review`: the `code-review` plugin, or GitHub CLI for PR review
- For `/sdlc:evals`: `claude plugin eval` (bundled with Claude Code)
