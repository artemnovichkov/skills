---
name: xcproj
description: Create, read, edit and validate Xcode projects from the command line with the `xcodeproj` and `xcprojformatter` tools that ship in Xcode 27.2+ — targets, build phases, build settings, groups and synchronized folders, xcconfig files, Swift packages, app extensions — plus the JSON `project.xcproj` format itself for the few things no command covers. Use this skill whenever a task touches an `.xcodeproj`, in either format (`project.xcproj` or legacy `project.pbxproj`): adding or removing a target, test bundle, framework, extension or Swift package, changing build settings per target or per configuration, wiring an xcconfig file, adding a run-script phase, creating a project from scratch, resolving a merge conflict in a project file, or checking one in CI. Reach for it even when the user never names these tools and just says "add X to the project" — editing a project file by hand instead is how agents silently corrupt them.
---

# xcproj

Xcode 27.2 ships two command-line tools for project files, neither on `PATH`:

- **`xcrun xcodeproj`** — reads and writes `.xcodeproj` bundles: targets, build
  phases, groups, build settings, xcconfig links, Swift packages. Works on
  **both** project formats and preserves the one it finds.
- **`xcrun xcprojformatter`** — parses a JSON `project.xcproj` and prints it in
  canonical form. Its real use is validation: see [Validate](#validate).

## Preflight

```sh
xcodebuild -version                                       # need 27.2+
[ "$(xcrun --find xcodeproj)" = "$(xcode-select -p)/usr/bin/xcodeproj" ] && echo OK
```

Always invoke as `xcrun xcodeproj`. A bare `xcodeproj` often resolves to the
CocoaPods Ruby gem of the same name, which takes completely different
arguments and will happily do something else. If the selected Xcode is older
than 27.2, neither tool exists — say so and stop rather than falling back to
hand-editing, which is how project files get quietly broken.

For a run of several commands, set the project once instead of repeating `-P`:

```sh
export XCODEPROJ_PROJECT=App.xcodeproj
```

## Use the CLI, not an editor

Project files look like plain data, which makes editing them directly
tempting. Resist it for anything a command covers:

- The CLI generates object IDs, keeps the Products group in sync, rejects
  dependency cycles, and validates *before* writing, so a rejected command
  leaves the file untouched.
- Its output is already canonical, so diffs stay minimal and reviewable. (A
  CLI edit needs no reformatting afterwards — verified.)
- `project.pbxproj` is an object graph with cross-referenced IDs. Hand-editing
  it is never acceptable.
- `project.xcproj` is readable JSON, but Xcode **silently drops keys it does
  not recognize**. A typo like `"buld-settings"` produces no error at all — the
  setting simply vanishes on the next save.

Hand-edit only for what no command expresses — per-file compiler flags, build
rules, variant groups, `localizations`, a target's `membership-exceptions` —
and when resolving a merge conflict. Then read
[references/format.md](references/format.md) for the exact keys, and validate.

## Read the help before first use of a command

Each command's help is long and unusually specific: it explains the edge cases,
lists the valid values, and names the command to use instead when you picked
the wrong one. It is also generated from the installed tool, so it is more
current than this skill.

```sh
xcrun xcodeproj help target phase add-copy     # or: ... add-copy --help
```

Error messages are written the same way — they list available targets, files,
or configurations, and suggest the fix. When a command fails, read the whole
message before changing the approach; it usually contains the answer.

## Command map

What exists, so you know what to reach for. Details via `help`.

| Task | Command |
| --- | --- |
| Create an empty project | `init <path>.xcodeproj` (JSON format only) |
| List targets / one target's phases | `target list` · `target info --target T` |
| Add / remove a target | `target add NAME --product-type TYPE` · `target remove T` · `target add-aggregate` |
| Target dependency | `target add-dependency T DEP` · `target remove-dependency` |
| Build phase | `target phase add sources\|resources\|frameworks\|headers --target T` |
| Run script / copy files phase | `target phase add-script` · `target phase add-copy --destination …` |
| Inspect / reorder / drop a phase | `target phase info --target T N` · `phase move N --to M` · `phase remove N` |
| Browse the navigator tree | `group ls [PATH] [-R]` |
| Group, folder-synced group | `group add NAME [--parent P]` · `group add NAME --filesystem-path DIR` |
| File reference in a regular group | `group add-file PATH --group G` · `group remove-file` |
| Target membership | `group include [FILE] --group G --target T [--phase N]` · `group exclude …` |
| Header visibility | `group set-header-visibility FILE --group G --target T --visibility public` |
| Read build settings | `setting list [--target T] [--config C]` · `setting get KEY` |
| Write build settings | `setting set KEY VALUE` · `setting set-multi KEY V1 V2` · `setting unset KEY` |
| Link an xcconfig file | `config set FILE --group G [--target T] [--config C]` · `config unset` |
| Swift packages | `pkg list` · `pkg add URL --from 1.2.0` · `pkg add-local PATH` · `pkg remove` |
| Package products & plugins | `pkg link PRODUCT --package P --target T [--embed]` · `pkg unlink` · `pkg link-plugin` |

Ground rules that apply across commands:

- `-P/--project` goes **after** the subcommand words:
  `xcrun xcodeproj target list -P App.xcodeproj`, never before them.
- Build phases are addressed by a **live 1-based index** from `target info`,
  not by kind — a target can have several phases of the same kind, and every
  add/remove/move shifts the numbering. Re-run `target info` before each
  phase-indexed command.
- A value starting with `-` must follow a bare `--`, and `--target`/`--config`
  must come before it:
  `setting set --config Debug OTHER_SWIFT_FLAGS -- -warn-concurrency`.
- About two dozen settings are list-valued (`OTHER_LDFLAGS`,
  `HEADER_SEARCH_PATHS`, `ARCHS`, …) and only `set-multi` accepts them; every
  other key only `set`. Each command rejects the wrong kind and names the other
  one, so there is nothing to memorize.
- `setting get`/`list` print **raw** stored values: no `$(inherited)`, no
  xcconfig contents, no defaults. A key defined in a linked xcconfig reads as
  `(unset)` here, annotated with the file. For resolved values use
  `xcodebuild -showBuildSettings`.
- Output is prose tables, not JSON. Exit codes: 0 success, 1 domain error,
  64 usage error.

## Recipes

Each one below was run end to end on Xcode 27.2 (27B5038j) and builds.

### A new app project

`init` writes a valid but completely bare project: no targets, no phases, and
none of the settings Xcode's template would have added. Everything is explicit,
and the order matters — phases before group inclusion (see
[Gotchas](#gotchas)).

```sh
mkdir -p Weather && cat > Weather/WeatherApp.swift <<'SWIFT'
import SwiftUI
@main struct WeatherApp: App { var body: some Scene { WindowGroup { Text("Hi") } } }
SWIFT
export XCODEPROJ_PROJECT=Weather.xcodeproj
xcrun xcodeproj init Weather.xcodeproj

# 1. Target, then its phases — nothing compiles without a sources phase,
#    and `pkg link` needs a frameworks phase to put the product in.
xcrun xcodeproj target add Weather --product-type application
xcrun xcodeproj target phase add sources --target Weather
xcrun xcodeproj target phase add frameworks --target Weather

# 2. A synchronized folder, so new files on disk never need a project edit.
xcrun xcodeproj group add Weather --filesystem-path Weather
xcrun xcodeproj group include --group /Weather --target Weather

# 3. Platform and language. Without SWIFT_VERSION the build fails; without a
#    deployment target it silently becomes "latest SDK only".
xcrun xcodeproj setting set SDKROOT iphoneos
xcrun xcodeproj setting set IPHONEOS_DEPLOYMENT_TARGET 18.0
xcrun xcodeproj setting set SWIFT_VERSION 6.0
xcrun xcodeproj setting set ALWAYS_SEARCH_USER_PATHS NO   # else every build warns

# 4. Bundle ID — the app builds without one, but `simctl install` rejects it.
xcrun xcodeproj setting set PRODUCT_BUNDLE_IDENTIFIER com.example.weather --target Weather
xcrun xcodeproj setting set INFOPLIST_KEY_UILaunchScreen_Generation YES --target Weather

xcodebuild -scheme Weather -destination 'generic/platform=iOS Simulator' build
```

`target add` seeds only `PRODUCT_NAME` and (for app/framework/bundle/test
types) `GENERATE_INFOPLIST_FILE`, so no `Info.plist` file is needed. It never
creates a scheme or workspace — `xcodebuild` generates a scheme per target
automatically, which is why the build above works. Copy platform settings from
a sibling target (`setting list --target App`) when adding to an existing
project instead of inventing values.

### A unit test target

Xcode's New Target sheet does more than `target add`; without the host wiring
`@testable import` fails to link.

```sh
xcrun xcodeproj target add WeatherTests --product-type unit-test-bundle
xcrun xcodeproj target phase add sources --target WeatherTests
xcrun xcodeproj group add WeatherTests --filesystem-path WeatherTests
xcrun xcodeproj group include --group /WeatherTests --target WeatherTests
xcrun xcodeproj target add-dependency WeatherTests Weather

# Run the tests inside the app and link against its binary.
xcrun xcodeproj setting set TEST_HOST \
  '$(BUILT_PRODUCTS_DIR)/Weather.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/Weather' --target WeatherTests
xcrun xcodeproj setting set BUNDLE_LOADER '$(TEST_HOST)' --target WeatherTests
xcrun xcodeproj setting set --config Debug ENABLE_TESTABILITY YES
```

`ENABLE_TESTABILITY` is already on in projects from Xcode's templates, but not
in one from `init`. With auto-generated schemes this is all it takes — verified
with both `-scheme Weather` and `-scheme WeatherTests` (`xcodebuild -list`
doesn't print the test scheme, but it works). A `PRODUCT_BUNDLE_IDENTIFIER` on
the test bundle is optional; tests run without one. What the CLI can't do is
touch a **shared** scheme: if the project has `xcshareddata/xcschemes`, its
Test action won't know about the new bundle until you add it in Xcode.

### Swift packages

```sh
xcrun xcodeproj pkg add https://github.com/pointfreeco/swift-dependencies \
  --from 1.9.0 --product Dependencies --target Weather
xcrun xcodeproj pkg add-local ../Packages/Core --product Core --target Weather
xcrun xcodeproj pkg link Algorithms --package swift-algorithms --target Weather --embed
xcrun xcodeproj pkg list
```

One requirement flag per package: `--from` (up to next major),
`--up-to-next-minor`, `--exact`, `--range-min`/`--range-max`, `--branch`,
`--revision`. `--product`/`--target` on `add` is shorthand for a follow-up
`pkg link`; both or neither. Packages need the target's frameworks phase to
exist, and resolve only in a **scheme** build (`xcodebuild -scheme`), not
`-target`. For a build-tool plugin use `pkg link-plugin` — a plugin is a
dependency, not a linked product, and is never embedded.

### Many settings at once: an xcconfig file

`setting set` takes one key per call. Beyond a handful, put them in a file —
easier to review, and it survives target churn:

```sh
mkdir -p Config && cat > Config/Project.xcconfig <<'CFG'
SDKROOT = iphoneos
IPHONEOS_DEPLOYMENT_TARGET = 18.0
SWIFT_VERSION = 6.0
CFG
xcrun xcodeproj group add Config
xcrun xcodeproj group add-file Project.xcconfig --group /Config
xcrun xcodeproj config set Project.xcconfig --group /Config
```

The xcconfig must live in a **regular** group, not inside a synchronized
folder (see [Gotchas](#gotchas)). A project-level xcconfig reaches every
target, including test bundles added later, so keep per-target values like the
bundle ID on the target. There is no `config get`: `setting get`/`list`
annotate each configuration with the xcconfig backing it.

### A framework target, linked and embedded

```sh
xcrun xcodeproj target add Core --product-type framework
for k in sources frameworks resources; do xcrun xcodeproj target phase add $k --target Core; done
xcrun xcodeproj group add Core --filesystem-path Core
xcrun xcodeproj group include --group /Core --target Core
xcrun xcodeproj setting set DYLIB_INSTALL_NAME_BASE @rpath --target Core
xcrun xcodeproj setting set SKIP_INSTALL YES --target Core
xcrun xcodeproj setting set PRODUCT_BUNDLE_IDENTIFIER com.example.core --target Core

xcrun xcodeproj target add-dependency Weather Core
xcrun xcodeproj target info --target Weather          # find the frameworks phase index
xcrun xcodeproj group include Core.framework --group Products --target Weather --phase 2
xcrun xcodeproj target phase add-copy --target Weather --destination frameworks --name "Embed Frameworks"
xcrun xcodeproj target info --target Weather          # the copy phase's new index
xcrun xcodeproj group include Core.framework --group Products --target Weather --phase 3
xcrun xcodeproj setting set-multi LD_RUNPATH_SEARCH_PATHS --target Weather -- \
  '$(inherited)' '@executable_path/Frameworks'
```

Two settings on the framework target are easy to miss, and both fail in a way
that doesn't name them:

- Without `PRODUCT_BUNDLE_IDENTIFIER`, `GENERATE_INFOPLIST_FILE` produces an
  Info.plist with no `CFBundleIdentifier`, and the *app's* embed phase fails
  with `Framework … did not have a CFBundleIdentifier in its Info.plist`.
- Without `DYLIB_INSTALL_NAME_BASE`, the install name stays
  `/Library/Frameworks/…`; the app builds and links fine, then crashes at
  launch. Verify with
  `otool -D <App.app>/Frameworks/Core.framework/Core` — it should print
  `@rpath/Core.framework/Core` — and launch the app, because building is not
  enough for embedded content.

## Building and testing what you changed

Two destinations, for two different needs — guessing a device name here is the
most common way to lose a cycle, since the names in Xcode's release notes are
rarely the ones installed:

```sh
# Building needs no real device:
xcodebuild -scheme App -destination 'generic/platform=iOS Simulator' build

# Running tests does. Take a UDID from what's actually installed:
xcrun simctl list devices available
xcodebuild test -scheme App -destination 'platform=iOS Simulator,id=<UDID>'
```

Simulator builds need no signing flags — reach for `CODE_SIGNING_ALLOWED=NO`
only if a build actually fails on signing. A test run that fails once with
`Test crashed with signal kill while preparing to run tests` is usually the
simulator's cold start, not the project: boot it first
(`xcrun simctl boot <UDID>`) or just re-run before changing anything.

## Validate

Cheap, and worth doing after any structural change:

```sh
python3 <skill-dir>/scripts/check.py App.xcodeproj --list
```

It runs, as applicable to the format:

1. **`xcprojformatter`** (JSON only) — fails on malformed JSON or an invalid
   value, with a path like `/targets[0]` on the first error.
2. **a canonical-form diff** — the only way to catch keys Xcode would silently
   drop. A hand-written `"build-setings"` shows up as a removed line. This is
   the check that matters after a hand edit or a merge; after a CLI-only edit
   it is always clean.
3. **`xcodebuild -list`** (with `--list`) — proves Xcode can actually load the
   project: unresolved target names, bad references, duplicate names.

Then build the affected scheme when the change touches compilation, and launch
the app when it touches embedded frameworks or resources.

In CI, fail the build when the file isn't canonical — that catches hand edits
that skipped the formatter:

```sh
for p in $(git ls-files '*.xcodeproj/project.xcproj'); do
  xcrun xcprojformatter "$p" | diff -u "$p" - || exit 1
done
```

## Gotchas

Verified on 27B5038j; all of them fail quietly rather than loudly.

**Add build phases before including a synchronized group.** If a target gains
its sources phase *after* a synchronized group was included, every file in the
folder lands in that target's `membership-exceptions` → `exclusions`. Nothing
compiles, and the build fails at link time with no mention of exclusions.
Re-including the group reports "already included"; include each file instead,
or add the phases first:

```sh
xcrun xcodeproj group include WeatherApp.swift --group /Weather --target Weather
```

**Keep xcconfig files out of synchronized folders.** `config set` refuses to
link one that lives inside a synchronized group's directory, and says so at
length. Put them in a regular group.

**An unknown `--product-type` is stored verbatim.** The CLI accepts any
fully-qualified `com.apple.product-type.*` string so new types keep working, so
a typo only fails much later, during the build. Use a short name
(`application`, `framework`, `library.static`, `unit-test-bundle`,
`ui-test-bundle`, `tool`, `app-extension`, … — `help target add` lists them) or
copy the identifier from a working target.

**`target remove` doesn't cascade.** It refuses while another target depends on
the one being removed; drop those edges with `target remove-dependency` first.
It does clean up the product reference and embed memberships by itself.

**Converting formats replaces the file.** Commit first.

```sh
xcodebuild -project App.xcodeproj -convert-project xcproj     # plist → JSON
xcodebuild -project App.xcodeproj -convert-project pbxproj    # JSON → plist
```

Both directions work in 27.2, and a named version (`"Xcode 27.0"`) works as a
synonym for the plist side. Before converting a real project, flag that tools
which parse `project.pbxproj` directly — CocoaPods, some fastlane actions,
XcodeGen/Tuist post-processing, in-house scripts — may break, often silently
with exit code 0. Schemes, `Package.resolved` and `xcuserdata` are unaffected,
and JSON projects still open in Xcode 27.0/27.1, so a team doesn't have to
upgrade in lockstep. The CLI tools, though, ship only with 27.2.

## What the CLI won't do

- **Schemes and workspaces.** It says so itself. `xcodebuild` auto-generates a
  scheme per target; shared schemes in `xcshareddata/xcschemes` are plain XML
  to edit, or use Xcode.
- **Duplicate a target.** Read the source target with
  `target info` + `setting list` and replay the commands.
- **Per-file compiler flags, build rules, variant groups, `localizations`.**
  Hand-edit with [references/format.md](references/format.md).
- **Resolve build settings.** `xcodebuild -showBuildSettings`.
- **Convert formats.** `xcodebuild -convert-project`.

For a custom check that the CLI can't express — "every target's deployment
target is at least 18" — read the project with Apple's
[xcode-project-format](https://github.com/apple/xcode-project-format) package
(`XCSchema` value types) instead of parsing JSON by hand.

## Hand-editing and merge conflicts

[references/format.md](references/format.md) documents the JSON format: every
key, path bases (`<PRODUCTS>`, `<SDK>`, `<DEVELOPER>`, …), name paths,
dependencies, build rules, variant groups, and the conflict-resolution rules.
Read it before writing a key that isn't in a recipe above — a wrong key fails
silently — and whenever a merge conflict lands in `project.xcproj`.

The short version for conflicts: resolve it, then run the canonical diff from
[Validate](#validate) before trusting it. Keeping both sides of a conflicted
*array* entry is the trap — it produces one object with two `repository` keys,
the formatter accepts it, and the project quietly loses a package.
