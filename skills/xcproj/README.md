# xcproj

Read, edit, and validate Xcode projects in the JSON project format (`project.xcproj`) introduced in Xcode 27.2.

Xcode silently ignores unknown keys — a typo means a lost setting with no error. This skill gives agents a format reference based on Apple's [xcode-project-format](https://github.com/apple/xcode-project-format) implementation, recipes verified in Xcode, and a validation script.

## Features

- **Format reference** — keys, values, path bases, and name paths for targets, files, folders, build phases, packages, dependencies
- **Recipes** — build settings, sources and folder exceptions, new targets, framework embedding, test targets, Swift packages, run scripts, xcconfig files (including inside synchronized folders)
- **Validation** — `scripts/check.py` runs `xcprojformatter`, reports keys Xcode would drop, and checks the project loads with `xcodebuild -list`

## Requirements

- macOS with Xcode 27.2 or later
- Python 3 (standard library only)
- Project converted to the JSON format (File inspector → Project Format → JSON)

## Usage

Ask your agent to change the project:

- "add a Networking framework target and embed it in the app"
- "add swift-collections and link DequeModule to the app"
- "exclude Legacy/Old.swift from the app target"
- "set SWIFT_STRICT_CONCURRENCY to complete for Debug only"
- "add a SwiftLint run script phase"

Validate manually:

```sh
python3 skills/xcproj/scripts/check.py App.xcodeproj --list
```

```
WARN keys dropped by Xcode (typo, wrong location, or default value):
  /targets[Kit]/buld-settings = {}
OK   xcodebuild -list
```

## Compatibility

Works with any agent that supports skills (Claude Code, Codex, Cursor, Xcode agents). Verified against Xcode 27.2 (27B5019j); the format may change in later versions.

A JSON Schema matching Apple's implementation, for editor autocompletion or CI, is available [as a gist](https://gist.github.com/artemnovichkov/0033fa6ca7d77312bbc7c8b7d6d7d350).
