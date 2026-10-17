# xcproj

Create, read, edit and validate Xcode projects from the command line with the
two tools that ship in Xcode 27.2+ — `xcrun xcodeproj` and
`xcrun xcprojformatter` — plus the JSON `project.xcproj` format itself for the
few things no command covers.

Agents don't reach for these tools on their own: they're new, they're not on
`PATH`, and no model has seen them in training data. Left alone, an agent edits
the project file as text — where Xcode silently drops any key it doesn't
recognize, so a typo costs you a build setting with no error anywhere. This
skill routes the work through the CLI, which generates IDs, validates before
writing, and leaves the file canonical, and keeps the format reference for the
cases that genuinely need a hand edit.

## Features

- **CLI first** — a map of every `xcodeproj` command plus the ground rules that
  aren't obvious from `--help` (flag placement, live phase indices, `--` before
  dash-leading values, raw vs. resolved settings)
- **Verified recipes** — a buildable iOS app from `init`, a unit test target with
  host wiring, Swift packages, xcconfig files, a framework target linked and
  embedded. Each one was run end to end on Xcode 27.2 (27B5038j)
- **Gotchas that fail quietly** — synchronized-group exclusions, a framework
  with no `CFBundleIdentifier`, unvalidated product types, format conversion
- **Validation** — `scripts/check.py` runs `xcprojformatter`, reports keys Xcode
  would drop, and checks the project loads with `xcodebuild -list`; works on
  both project formats
- **Format reference** — `references/format.md`: every key and value from
  Apple's [xcode-project-format](https://github.com/apple/xcode-project-format),
  plus merge-conflict rules

## Requirements

- macOS with Xcode 27.2 or later selected (`xcode-select -p`)
- Python 3 (standard library only), for `scripts/check.py`

Both project formats are supported. `project.xcproj` (JSON) gets the full set of
checks; a legacy `project.pbxproj` is edited by the same CLI but can only be
verified by loading it.

## Usage

Ask your agent to change the project:

- "create an iOS app project from scratch, no Xcode"
- "add a Networking framework target and embed it in the app"
- "add swift-collections and link DequeModule to the app"
- "move SWIFT_VERSION and the deployment target into an xcconfig"
- "add a unit test target that can `@testable import` the app"
- "resolve this merge conflict in project.xcproj"

Validate by hand:

```sh
python3 skills/xcproj/scripts/check.py App.xcodeproj --list
```

```
WARN keys dropped by Xcode (typo, wrong location, or default value):
  /targets[Kit]/buld-settings = {}
OK   xcodebuild -list
```

In CI, fail when a project file isn't canonical — that catches hand edits that
skipped the formatter:

```sh
for p in $(git ls-files '*.xcodeproj/project.xcproj'); do
  xcrun xcprojformatter "$p" | diff -u "$p" - || exit 1
done
```

## Compatibility

Works with any agent that supports skills (Claude Code, Codex, Cursor, Xcode
agents). Verified against Xcode 27.2 (27B5038j); the format and both tools are
still in beta and may change.

A JSON Schema matching Apple's implementation, for editor autocompletion or CI,
is available [as a gist](https://gist.github.com/artemnovichkov/0033fa6ca7d77312bbc7c8b7d6d7d350).
