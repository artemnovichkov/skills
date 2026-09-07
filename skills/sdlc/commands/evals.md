---
description: Build a regression suite for the repo's agent configuration - CLAUDE.md, skills, and hooks - and run it in CI.
allowed-tools: Bash(claude plugin eval:*), Bash(ls:*), Bash(git log:*)
---

# Stage 4B — Continuous evals for agent configuration

`CLAUDE.md`, skills, and hooks are code that steers every session. They regress silently. Evals are the regression suite for them.

## Workflow

### 1. Collect real cases

Do not invent prompts. Pull 20–50 tasks the repo actually saw:

- Recent commits and PR titles (`git log --oneline -100`) — real change shapes
- Corrections already recorded in `CLAUDE.md` — each one is a case that should now pass
- Past incidents or bugs — each becomes a permanent case

Start with 5–10 good cases rather than 50 vague ones. Coverage grows by accretion.

### 2. Scaffold the suite

Use the built-in eval runner rather than hand-rolling one:

```
claude plugin eval init            # interview-driven suite authoring
claude plugin eval init --bare <name>   # blank single-case template
```

Cases live under `evals/` as `case.yaml` (or `prompt.md` + `graders/*.md`). Write each as a prompt plus acceptance checks: tests pass, lint clean, behaviour unchanged, the repo's policy followed.

If the target is a repo's `.claude/` configuration rather than a packaged plugin, and the runner cannot resolve it, fall back to a shell runner over `claude -p` — one non-interactive run per case, asserting the same checks — and say clearly that this is the fallback.

### 3. Run and record

```
claude plugin eval . --threshold 0.8
```

Record the current pass rate as the baseline. Add `evals/results/` to `.gitignore` — run output is not source. A case that already fails is a finding, not a broken eval — either the config needs fixing or the case is wrong. Decide which, explicitly.

### 4. Wire into CI

Write `.github/workflows/sdlc-evals.yml` from `${CLAUDE_PLUGIN_ROOT}/templates/ci/sdlc-evals.yml`:

- Runs on pull requests touching `CLAUDE.md`, `.claude/**`, `evals/**`
- Runs on a schedule (weekly is enough to start)
- Fails below the threshold, so config changes are gated on it

Evals cost money to run. Say so, keep `--runs` low in CI, and mention `--max-cost-usd` for a hard ceiling.

### 5. Keep it fed

Every production incident becomes a permanent case once its fix ships. That is the mechanism that stops the same class of failure returning.
