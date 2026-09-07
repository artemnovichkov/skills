# <Title> — Implementation Plan

Status: draft
Intent: sdlc/intent/<slug>.md
Spec: sdlc/spec/<slug>.md
Date: <YYYY-MM-DD>

## Files to change

| File | Change | Why |
| --- | --- | --- |
| `path/to/file` | <what changes> | <which requirement it serves> |

## Reuse

<Existing functions, utilities, and patterns this builds on, with paths. If
this section is empty in a mature repo, look again.>

## Work order

1. <step> — <what it depends on>
2. ...

## Tests required

| Test | Asserts | New or existing |
| --- | --- | --- |
| <name> | <behaviour> | new / existing |

Done condition: <quantifiable - which tests pass, what the build produces,
what the UI shows>

## What could break

<Neighbouring behaviour, callers, migrations, platform edges. Be specific
enough that the verifier knows what to exercise.>

## Interrogation

- **What breaks if this ships as written?** <answer>
- **Riskiest step, and what de-risks it?** <answer>
- **Best alternative, and why not it?** <answer>

## Rollback

<How this gets undone if it goes wrong in production.>
