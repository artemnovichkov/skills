---
description: Wire production metrics back into the loop with control bands - deterministic detection, tiered response, stage 6.
allowed-tools: Bash(ls:*), Bash(git log:*)
---

# Stage 6 — Close the loop

Production signal becomes a new intent instead of a ticket someone notices on Monday. Detection stays deterministic; the model is only invoked once a band is breached.

## Workflow

### 1. Pick one metric

Start with a single metric that already exists and already matters: CI failure rate, crash-free sessions, p95 latency, error rate. One metric wired end to end beats five half-wired.

Ask where it can be read from without new infrastructure — CI API, Crashlytics, an existing dashboard's API, a log query.

### 2. Define the bands

Write `sdlc/bands.yaml` from `${CLAUDE_PLUGIN_ROOT}/templates/bands.yaml`:

- Baseline: a rolling window (30 days is a reasonable default)
- `1σ` → log only
- `2σ` → invoke Claude **read-only** to diagnose (Read, Grep, and specific read-only Bash queries)
- `3σ` → Claude may act, and only through pre-approved routes: open a pull request, or run a named runbook

Detection is arithmetic — mean and standard deviation, or Western Electric rules. Keep it in the watcher script, out of the model.

### 3. Write the watcher

A small script that reads the metric, compares against the baseline, and on breach invokes `claude -p` with the tier's tool restrictions. It runs on a schedule (cron, or a CI schedule). No production credentials; read-only tokens only.

### 4. Route the output

At tier 2 the diagnosis is written as `sdlc/intent/<slug>.md` in the stage 1 format — that is the loop closing. The user triages it like any other intent: small fixes go straight to `/sdlc:plan`, larger ones get a spec first.

At tier 3, action is bounded to a PR or a named runbook. Nothing merges or deploys without a human. Rehearse the rollback path before it is needed.

### 5. Prevent the repeat

When a fix ships, add an eval case for that incident class (`/sdlc:evals`). Repeat incidents of the same class are the metric that says whether this stage is working.
