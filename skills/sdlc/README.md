# sdlc Skill

An artifact-driven software lifecycle. Each stage produces one markdown file in `sdlc/`, committed to git, that triggers the next stage.

Adapted from Anthropic's [AI-Native SDLC Playbook](https://claude.com/blog/the-ai-native-sdlc-playbook), trimmed for a solo developer — the artifact chain and the verification discipline, without the org apparatus. The org layer is kept in `references/governance.md` and is opt-in.

## The chain

```
sdlc/intent/<slug>.md   what problem, why now, constraints, open questions
sdlc/spec/<slug>.md     requirements + design, concerns flagged
sdlc/plan/<slug>.md     files to change, work order, tests required
<diff> + tests          verified before a human looks
PR + REVIEW.md passes   reviewed against the spec and the plan
production signal       becomes a new intent, loop restarts
```

One slug runs through all three files, so `git log sdlc/*/<slug>.md` is the full decision history for a change.

## Features

- **Eight commands, one per stage** — from capturing an idea to wiring production alerts back into planning
- **Templates that ask real questions** — intent, spec, plan, `REVIEW.md`, `bands.yaml`, `CLAUDE.md` sections
- **`verifier` subagent** — runs the app, exercises the change and its neighbours, reports what actually worked, fixes nothing
- **Test-file lock** — an opt-in hook that blocks editing tests during a bug fix, so the fix cannot be made to pass by weakening the check
- **Reuses what exists** — plan mode for planning, `/code-review` for review, `claude plugin eval` for config evals

## Commands

| Command | Stage | Produces |
| --- | --- | --- |
| `/sdlc:init` | setup | `sdlc/` scaffold, `REVIEW.md`, `CLAUDE.md` sections |
| `/sdlc:intent` | 1. Plan | `sdlc/intent/<slug>.md` |
| `/sdlc:spec` | 2. Design | `sdlc/spec/<slug>.md` |
| `/sdlc:plan` | 3. Build | `sdlc/plan/<slug>.md` |
| `/sdlc:verify` | 4. Test | verification report, optional test lock |
| `/sdlc:evals` | 4. Test | `evals/` suite + CI workflow |
| `/sdlc:review` | 5. Deploy | `REVIEW.md`, then `/code-review` |
| `/sdlc:bands` | 6. Maintain | `sdlc/bands.yaml` + watcher |

## Usage

```
/sdlc:init                      # once per repo, pick what to enable
/sdlc:intent add offline mode   # -> sdlc/intent/offline-mode.md
/sdlc:spec offline-mode         # -> sdlc/spec/offline-mode.md
/sdlc:plan offline-mode         # -> sdlc/plan/offline-mode.md, then implement
/sdlc:verify                    # run the loop, report real output
/sdlc:review                    # policy-driven review of the diff
```

Every command drafts, then hands the draft back for correction. Nothing is committed automatically — each command prints the commit command and waits.

Stages are useful alone. Starting with `/sdlc:intent` and `CLAUDE.md` and adding the rest later is the normal path.

## The test lock

```
/sdlc:verify --lock-tests     # creates sdlc/.lock-tests
/sdlc:verify --unlock-tests   # removes it
```

While the marker exists, the bundled `PreToolUse` hook blocks edits to test files (`*Tests.swift`, `*_test.go`, `*.spec.ts`, anything under `Tests/`, `tests/`, `__tests__/`, …). Without the marker the hook exits silently, so ordinary test writing is never affected.

## Requirements

- Git repository
- `CLAUDE.md` at repo root — `/sdlc:init` creates or extends it
- Optional: the [`code-review`](https://github.com/anthropics/claude-plugins-official) plugin for `/sdlc:review`
- Optional: `claude plugin eval` (bundled with Claude Code) for `/sdlc:evals`
- Optional: `gh` CLI for PR review

## Agent compatibility

- **Claude Code** — full support: commands, subagent, hook
- **Other agents (via [skills.sh](https://skills.sh))** — `SKILL.md`, templates, and references work; slash commands, the subagent, and the hook are Claude Code specific. The workflow can still be driven by asking for a stage by name.

## Not in scope

The playbook's organisation-level pieces cannot ship in a plugin and are set up centrally: managed settings via MDM, scheduled security scanning, and Slack incident response. `references/governance.md` describes how they relate to the stages here.
