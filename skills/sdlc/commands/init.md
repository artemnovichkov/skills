---
description: Scaffold the SDLC artifact chain in this repo - sdlc/ directories, REVIEW.md, and CLAUDE.md sections.
allowed-tools: Bash(git status:*), Bash(git rev-parse:*), Bash(mkdir:*), Bash(ls:*)
---

# Initialize the SDLC loop

Set up an artifact-driven lifecycle in the current repository. Add only what the user asks for — do not dump twelve files on them.

## Workflow

### 1. Check the ground

- `git rev-parse --show-toplevel` — abort with an explanation if this is not a git repo.
- Check whether `sdlc/`, `REVIEW.md`, `CLAUDE.md`, `evals/` already exist. Never overwrite; extend or skip.
- Detect the project type (language, build tool, test runner) by reading manifests: `Package.swift`, `*.xcodeproj`, `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`.

### 2. Ask what to enable

Present the pieces and let the user pick (multi-select). Recommend the first two for anyone starting out:

1. **Artifact chain** (recommended) — `sdlc/intent/`, `sdlc/spec/`, `sdlc/plan/` + `sdlc/README.md` explaining the flow
2. **CLAUDE.md sections** (recommended) — verification commands with healthy output, plus a "Things Claude gets wrong" section
3. **Review policy** — `REVIEW.md` at repo root
4. **Config evals** — `evals/` suite and CI workflow (delegates to `/sdlc:evals`)
5. **Control bands** — `sdlc/bands.yaml` and watcher (delegates to `/sdlc:bands`)

### 3. Create the artifact chain

If selected, create `sdlc/intent/`, `sdlc/spec/`, `sdlc/plan/`, each with a `.gitkeep`, plus `sdlc/README.md` describing the chain and which command produces each file. Copy the stage templates from `${CLAUDE_PLUGIN_ROOT}/templates/` into `sdlc/templates/` **only if** the user wants to customise them; otherwise the commands read them from the plugin.

Add `sdlc/.lock-tests` to `.gitignore` — it is a local toggle for the test-file guard, not shared state.

### 4. Extend CLAUDE.md

If selected, append the sections from `${CLAUDE_PLUGIN_ROOT}/templates/claude-md-sections.md`, filled in for this repo:

- The real build / test / lint commands, discovered from the manifests in step 1. Run each once and paste a trimmed sample of healthy output so future sessions can recognise success.
- A quantifiable done-condition ("all tests in X pass", "zero lint warnings").
- An empty "Things Claude gets wrong" section with a one-line note on how it gets filled.

If `CLAUDE.md` already has a section with the same heading, leave it alone and report which sections you skipped.

### 5. Review policy

If selected, write `REVIEW.md` from `${CLAUDE_PLUGIN_ROOT}/templates/REVIEW.md`, adapted to this repo: name the generated paths to exclude, the CI-enforced rules not worth commenting on, and the project's actual security surface.

### 6. Hand off

Print a short summary: files created, files skipped and why, and the suggested commit command. Do not commit. Then tell the user the next step is `/sdlc:intent`.
