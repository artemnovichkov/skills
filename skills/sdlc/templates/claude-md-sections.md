<!--
Sections appended to a repo's CLAUDE.md by /sdlc:init.
Fill in the real commands and real output before committing - a placeholder
here is worse than nothing, because future sessions will trust it.
-->

## Verification

Run all of these before reporting any task complete.

| What | Command | Healthy output |
| --- | --- | --- |
| Build | `<command>` | `<trimmed real output>` |
| Test | `<command>` | `<trimmed real output>` |
| Lint | `<command>` | `<trimmed real output>` |

Done condition: <quantifiable - e.g. "all tests in FooTests pass, zero lint warnings">

<!-- Example for a Swift package:
| Build | `swift build` | `Build complete! (2.31s)` |
| Test  | `swift test`  | `Executed 42 tests, with 0 failures` |
| Lint  | `swiftlint`   | `Done linting! Found 0 violations` |
-->

## Things Claude gets wrong

Corrections that had to be made more than once. When the same correction comes
up a second time, it goes here instead of being made by hand again.

- <correction>
