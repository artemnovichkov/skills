# Stages in detail

Reference for the six stages. Load when a command needs more than its own workflow — the measurement questions, the reasoning behind a rule, or the setup order.

Adapted from Anthropic's [AI-Native SDLC Playbook](https://claude.com/blog/the-ai-native-sdlc-playbook).

---

## 1. Plan — capture as intent

**What changes.** Ideas enter the system as machine-readable documents instead of living in a head, a chat thread, or a meeting.

**Artifact.** `sdlc/intent/<slug>.md` — problem, proposed outcome, affected systems, constraints, open questions.

**Why it earns its cost.** The intent is the cheapest place to be wrong. Rewriting a paragraph costs minutes; rewriting a feature costs days. It also survives context loss — a session three weeks later starts from the intent rather than from a summary of a summary.

**Worth watching.** How long from first conversation to a written intent. How many intents survive to a spec — a low rate is not failure, it means the stage is doing its filtering job cheaply.

---

## 2. Design — requirements and design in one session

**What changes.** Analysis and design collapse into one pass, and policy gets applied while the spec is written rather than discovered in review later.

**Artifact.** `sdlc/spec/<slug>.md` — requirements, design, alternatives, flagged concerns.

**The flagging discipline.** The value is in what gets flagged, not in what gets written. A spec that silently resolves a collision with a repo convention has hidden a decision. A spec that flags it forces the decision into the open, where it is recorded.

**Worth watching.** Requirements rework after the build starts — commits to `spec.md` dated after the first `plan.md` are the direct measure.

---

## 3. Build — nothing implemented without an accepted plan

**What changes.** Design review happens before code generation instead of in the PR.

**Artifact.** `sdlc/plan/<slug>.md` — files to change, work order, tests required.

**Plan mode.** Claude Code's plan mode (`shift+tab`) makes the read-only constraint technical rather than a promise. Use it.

**Plan drift.** If implementation departs from the plan, the plan is updated in the same commit as the code. A plan that no longer describes the code is worse than no plan, because it is trusted.

**The supporting cast.**

- **`CLAUDE.md`** carries what the repo knows: build and test commands with healthy output, conventions, architecture, and the mistakes worth not repeating. Rule: when the same correction is needed twice, it goes in the file.
- **Skills** carry knowledge that must apply consistently across sessions or repos — a security review checklist, a house style, a compliance rule. `.claude/skills/<name>/SKILL.md`, checked into git, reviewed like code.
- **Hooks** carry what must hold without exception. Skills advise; hooks enforce. Anything whose violation is genuinely unacceptable needs a hook behind the skill. Keep them fast and scoped to the changed file — heavy checks belong at PR time.
- **Subagents** are scoped helpers with their own context and tool limits. The `verifier` bundled here is the canonical one: it exercises behaviour and reports, and it never fixes.
- **Parallel sessions** run in separate git worktrees on independent tasks. Independence is the requirement — two sessions on overlapping files produce merge pain that costs more than the parallelism saved.

**Worth watching.** Share of changes that merge on the first implementation pass. How often the merged diff matches the committed plan.

---

## 4. Test — every session checks its own work

**The feedback loop (4A).** Always give the session a way to verify before a human sees the change.

1. Wrap verification in one command (`make test`, `swift test`, `npm test`).
2. List it in `CLAUDE.md` with an example of healthy output.
3. State a quantifiable target — "all tests in X pass", not "tests look good".
4. For bug fixes: write the failing test first, commit it, then fix the code without touching the test.
5. For UI: give the session a way to see the result — screenshot, preview, driven run — and iterate two or three rounds.
6. Require all checks to run before anything is reported complete.

**The test lock.** The bundled `PreToolUse` hook blocks edits to test files while `sdlc/.lock-tests` exists, so a fix cannot be made to pass by weakening the check. It is inert without the marker file — ordinary test writing is never blocked.

**Config evals (4B).** `CLAUDE.md`, skills, and hooks steer every session and regress silently. Evals are their regression suite: 20–50 real recent tasks, each written as a prompt plus acceptance checks, run non-interactively in CI on config changes and on a schedule. Gate config changes on the pass rate. Every production incident becomes a permanent case.

Use `claude plugin eval init` to author the suite rather than inventing a format.

**Worth watching.** First-pass CI success rate for agent-written changes. Time from incident to a permanent eval case.

---

## 5. Deploy — the same review, every time

**What changes.** Every change gets identical passes, so human attention rises to intent and risk.

**Artifact.** `REVIEW.md` — the passes, the Important/Nit line, the exclusions.

**Why write the policy down.** An unwritten review standard is re-argued in every PR and applied differently every time. Written once, it can be argued about once.

**The nit cap matters.** A review that returns thirty style comments trains everyone to skim reviews. Cap the nits; move the recurring ones into a linter or into `CLAUDE.md`.

**Boundary.** The agent does not approve its own work. It presents findings; a human decides what merges.

**Gates.** Deterministic checks belong at build time; approval gates belong at deploy time. Tier autonomy by environment — free in dev, restricted in staging, gated in production. The agent may act up to the production gate and not past it.

**Worth watching.** Time to first review. Defects caught before merge versus in production.

---

## 6. Maintain — the loop closes

**What changes.** A production signal becomes a new intent automatically instead of a ticket someone notices later.

**Artifact.** `sdlc/bands.yaml` — the metric, the baseline, the tiered response.

**Detection stays deterministic.** Mean and standard deviation, or Western Electric rules, computed in a script. The model is invoked only once a band is breached. Detection by LLM is expensive, non-reproducible, and impossible to tune.

**Tiers.** 1σ logs. 2σ invokes a read-only diagnosis that lands as `sdlc/intent/<slug>.md`. 3σ permits bounded action through pre-approved routes only — a pull request, or a named runbook. No production credentials at any tier.

**Prevent the repeat.** When a fix ships, add an eval case for that incident class. Repeat incidents of the same class are the metric that says whether this stage works.

---

## Setup order

Start with the pieces that have no prerequisites:

1. Capture as intent, `CLAUDE.md`, skills — useful on day one, no infrastructure
2. Plan mode → the build stage
3. Feedback loop → the test stage
4. Review policy → the deploy stage, then gates
5. Control bands → the maintain stage

Each stage is useful alone. The compounding comes from the chain, but the chain does not have to be complete to pay.
