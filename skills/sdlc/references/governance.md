# Governance layer (optional)

The commands in this skill are tuned for a solo developer: the artifact chain and the verification discipline, without the org-scale apparatus. This file holds the apparatus, for when a repo has more than one person in it or an auditor eventually asks.

Load it when the user mentions team standards, audit trails, compliance, policy owners, or separation of duties.

## Separation of duties

The agent does not approve its own work. Concretely:

- Branch protection turns agent actions into pull requests rather than pushes to the default branch.
- The review pass presents findings; a human approves and merges.
- Non-interactive runs act under their own identity, logged separately from a person's, so "who did this" has an answer.

## What gets versioned

Everything that steers a decision, in git, reviewed like code:

| Artifact | Where |
| --- | --- |
| Intent, spec, plan | `sdlc/` |
| Repo conventions | `CLAUDE.md` |
| Policy that must apply consistently | `.claude/skills/` |
| Rules that must hold without exception | `.claude/hooks/` or a plugin's `hooks.json` |
| Review policy | `REVIEW.md` |
| Alert thresholds and response tiers | `sdlc/bands.yaml` |
| Config regression suite | `evals/` |

The git history is the audit trail: who wrote which artifact, when, what changed between versions, and what the diff looked like at the moment of approval.

## Policy ownership

Each policy skill has an owner who signs off on changes to it. Skill changes go through review like code. The measure of whether this works: review findings that cite a policy should fall toward zero over time, because the policy is being applied during implementation rather than discovered afterwards.

## Advisory versus enforced

Skills advise; hooks enforce. Any policy whose violation is genuinely unacceptable — not merely undesirable — needs a hook behind the skill. Everything else stays advisory, because a hook that blocks legitimate work gets disabled, and a disabled hook enforces nothing.

## Evidence

Attach literal outputs to records, not summaries of them: test logs, screenshots, review findings, eval results. "Tests passed" in a PR description is an assertion; the pasted output is evidence.

## Environment tiering

Autonomy scales down as blast radius scales up:

- **dev** — free rein
- **staging** — restricted, write actions behind existing gates
- **production** — gated; the agent may act up to the gate and not past it

Agent jobs run in containers under a network policy with short-lived tokens, and no production credentials by default. Rehearse the rollback path before it is needed.

## Beyond a plugin

These parts of the playbook cannot be shipped as a plugin and are set up at the organisation level:

- **Managed settings via MDM** — a platform team deploys permission policy that engineers cannot override: denied paths and tools, a sandbox with a network allowlist, only managed hooks, only approved plugins from an org marketplace.
- **Recurring codebase scans** — scheduled security scanning whose findings flow through the same PR gate as any other change.
- **Claude in Slack** — an incident first responder whose channel thread becomes the audit trail.

## Measurement

Each stage has a leading indicator (fast, noisy, tells you the process is running) and a lagging one (slow, meaningful, tells you it is working). They are listed per stage in `stages.md`. Pick two or three total. A dashboard of twelve process metrics is a way of not looking at any of them.
