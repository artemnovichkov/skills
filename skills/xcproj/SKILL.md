---
name: xcproj
description: Read and edit Xcode projects in the JSON project format (`project.xcproj`, Xcode 27.2+) — add targets, Swift packages, files and folders, build phases, build settings, dependencies — and validate the result. The format is new and undocumented, so use this skill whenever an `.xcodeproj` contains `project.xcproj` instead of `project.pbxproj`, or the user mentions .xcproj, the JSON project format, or asks to change Xcode project configuration (targets, schemes aside) without opening Xcode, even if they don't name the format.
---

# xcproj

Edit Xcode's JSON project format (`App.xcodeproj/project.xcproj`) safely.

The format shipped in Xcode 27.2 with no public spec. Everything here is reverse-engineered from Xcode 27.2 (27B5019j). If Xcode's own tools disagree with this skill, trust the tools.

## Detect the format

```sh
ls App.xcodeproj
```

- `project.xcproj` → JSON format, use this skill.
- `project.pbxproj` → legacy plist format. There's no CLI converter; if the user wants JSON, tell them: select the project in the Project navigator → File inspector → Project Document → Project Format → JSON.
- Never create `project.pbxproj` next to `project.xcproj` — Xcode refuses to open a project with both.

## How the format thinks

The plist format was a flat graph of objects with IDs. The JSON format is a tree addressed by names, which is what makes it editable by hand. Keep these rules in mind:

- **Unknown keys are silently dropped.** A typo like `"buld-settings"` produces no error — the setting just disappears on the next save. This is the main risk when editing, so always run the check script afterwards.
- **Names are references.** Targets are referenced by `name`, build phases as `"Target/phase"`, products as a name path like `"Products/App.app"`. Renaming a target means updating every string that mentions it.
- **No build-file objects.** A file declares which build phases it belongs to via `target-membership`, instead of phases listing files.
- **IDs only where required.** Targets need an `"id"` (24 uppercase hex chars, unique in the file). Product file references carry one too. Don't add IDs anywhere else.
- **Defaults are omitted.** Xcode doesn't write `false`, empty arrays, `"kind": "native"`, `"scope": "always"`, etc.
- **Syntax is JSONC.** Trailing commas and `//` comments are accepted. Xcode rewrites the file on save, dropping comments, so don't rely on them.
- **Kebab-case keys.** The exception is dependency kinds: `localTarget`, `remoteTarget`.

Generate an ID:
```sh
uuidgen | tr -d - | cut -c1-24
```

## Workflow

1. Read `project.xcproj` fully before editing. Match the existing structure (groups vs folders, where packages and settings live).
2. Make the edit. Use the recipes below; for any key not covered, look it up in [references/format.md](references/format.md). Don't guess key names — a wrong key fails silently.
3. Validate:
   ```sh
   python3 <skill-dir>/scripts/check.py App.xcodeproj --list
   ```
   - `FAIL xcprojformatter` with a JSON path → malformed JSON or invalid value; fix at that path.
   - `WARN keys dropped` → typo, key in the wrong place, or a default value. Fix everything except defaults you added on purpose.
   - `FAIL xcodebuild -list` → Xcode can't load the project (unknown target name, bad reference, duplicate name).
4. Build the affected scheme when the change matters for compilation (new target, package, sources). For new frameworks or embedded content, also launch the app — linking problems like a wrong install name only show up at launch.
5. Optionally canonicalize so the diff matches what Xcode would write: `xcrun xcprojformatter --update App.xcodeproj`. Mention it to the user rather than doing it silently if the file had comments — they'll be removed.

## Recipes

### Build settings

Project-level settings live in the root `build-settings`, target-level ones in the target's `build-settings`. Conditions are key suffixes, not separate configuration objects:

```jsonc
"build-settings": {
  "SWIFT_VERSION": "6.0",
  "SWIFT_OPTIMIZATION_LEVEL[config=Debug]": "-Onone",
  "SWIFT_OPTIMIZATION_LEVEL[config=Release]": "-O",
  "OTHER_LDFLAGS[sdk=iphoneos*]": "-ObjC",
}
```

Values are strings; list-type settings are space-separated strings. Keep keys sorted — that's how Xcode writes them.

### Add a Swift file or folder of sources

Most projects use synchronized folders (`"kind": "folder"`): any file dropped into the directory is automatically part of the listed targets, so adding a file on disk needs no project edit.

New top-level folder for a target:
```jsonc
"files": [
  { "kind": "folder", "path": "Networking", "target-membership": [ "App" ] },
]
```

Exclude a file from a target, or add per-file compiler flags:
```jsonc
{ "kind": "folder", "path": "App", "target-membership": [ "App" ],
  "membership-exceptions": [
    { "target": "App",
      "exclusions": [ "Legacy/Old.swift" ],
      "compiler-flags": { "Bridge.m": "-fno-objc-arc" } },
  ] }
```

Individual file in a regular group, added to a target's phases:
```jsonc
{ "kind": "group", "path": "Support", "children": [
  { "path": "Helper.swift", "target-membership": [ "App/compile-sources" ] },
  { "path": "data.json", "target-membership": [ "App/resources" ] },
] }
```

### Add a target

```jsonc
{
  "name": "Kit",
  "id": "<24 hex>",
  "product": "Products/Kit.framework",
  "product-type": "framework",
  "build-phases": [ "headers", "compile-sources", "frameworks", "resources" ],
  "build-settings": {
    "DEFINES_MODULE": "YES",
    "DYLIB_INSTALL_NAME_BASE": "@rpath",
    "GENERATE_INFOPLIST_FILE": "YES",
    "LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks @loader_path/Frameworks",
    "PRODUCT_BUNDLE_IDENTIFIER": "com.example.Kit",
    "PRODUCT_NAME": "$(TARGET_NAME)",
    "SKIP_INSTALL": "YES",
    "SWIFT_VERSION": "6.0",
  },
}
```

A target also needs:
- a product reference in the products group, with its own ID:
  ```jsonc
  { "path": "<PRODUCTS>/Kit.framework", "id": "<24 hex>", "type": "wrapper.framework", "index": false }
  ```
- a sources folder: `{ "kind": "folder", "path": "Kit", "target-membership": [ "Kit" ] }`.

`product-type` drops the `com.apple.product-type.` prefix (any string passes validation, so a wrong value like `unit-test` only fails at build or test time): `application`, `framework`, `library.static`, `library.dynamic`, `tool`, `bundle.unit-test`, `bundle.ui-testing`, `app-extension`. Product `type` is the matching file type: `wrapper.application`, `wrapper.framework`, `archive.ar`, `wrapper.cfbundle`, `wrapper.app-extension`.

Copy platform settings (`SDKROOT`, deployment target, `TARGETED_DEVICE_FAMILY`) from an existing target when they aren't set at the project level. Don't copy an existing framework target blindly: hand-made projects often lack `DYLIB_INSTALL_NAME_BASE`, and without it the framework's install name is `/Library/Frameworks/…` — the app builds fine but fails to launch.

### Link and embed a framework target

On the app target add a dependency, an embed phase, and `"LD_RUNPATH_SEARCH_PATHS": "$(inherited) @executable_path/Frameworks"` so the embedded framework is found at launch; on the product reference declare membership in both phases:

```jsonc
// app target
"dependencies": [ "Kit" ],
"build-phases": [
  "compile-sources", "frameworks", "resources",
  { "kind": "copy", "name": "Embed Frameworks", "bundle-base-path": "frameworks-directory" },
],

// products group
{ "path": "<PRODUCTS>/Kit.framework", "id": "…", "type": "wrapper.framework", "index": false,
  "target-membership": [
    "App/frameworks",
    { "build-phase": "App/copy/Embed Frameworks", "code-sign-on-copy": true, "header-preservation": "remove-on-copy" },
  ] }
```

### Add a unit test target

```jsonc
{
  "name": "AppTests",
  "id": "<24 hex>",
  "product": "Products/AppTests.xctest",
  "product-type": "bundle.unit-test",
  "test-host-target": "App",
  "dependencies": [ "App" ],
  "build-phases": [ "compile-sources", "frameworks", "resources" ],
  "build-settings": {
    "BUNDLE_LOADER": "$(TEST_HOST)",
    "GENERATE_INFOPLIST_FILE": "YES",
    "PRODUCT_BUNDLE_IDENTIFIER": "com.example.AppTests",
    "PRODUCT_NAME": "$(TARGET_NAME)",
    "SWIFT_VERSION": "6.0",
    "TEST_HOST": "$(BUILT_PRODUCTS_DIR)/App.app/$(BUNDLE_EXECUTABLE_FOLDER_PATH)/App",
  },
}
```
Plus the `<PRODUCTS>/AppTests.xctest` product reference (`"type": "wrapper.cfbundle"`) and a sources folder. With auto-generated schemes, `xcodebuild test -scheme App` picks up the hosted test target; if the project has shared schemes (`xcshareddata/xcschemes`), add the target to the scheme's test action.

### Add a Swift package

Declare the package at the root, then link a product from the target:

```jsonc
"packages": [
  { "kind": "remote", "repository": "https://github.com/apple/swift-algorithms",
    "version": { "up-to-next-major-version": "1.2.0" } },
  { "kind": "local", "path": "Packages/Core" },
],

// in the target
"package-product-members": [
  { "package": "swift-algorithms", "product-name": "Algorithms", "build-phase": { "build-phase": "frameworks" } },
  { "product-name": "Core", "build-phase": { "build-phase": "frameworks" } },
],
```

- `package` is the repository's last path component without `.git`; omit it for local packages.
- `version`: exactly one of `up-to-next-major-version`, `up-to-next-minor-version`, `version` (exact), `branch`, `revision`, or `"version-range": "1.0.0..<2.0.0"`.
- Verify resolution with `xcodebuild -resolvePackageDependencies -project App.xcodeproj`.

### Add a run script phase

```jsonc
{ "kind": "script", "name": "SwiftLint",
  "shell": "/bin/sh",
  "script": "if command -v swiftlint >/dev/null; then swiftlint; fi\n",
  "input-paths": [ "$(SRCROOT)/.swiftlint.yml" ],
  "run-on-every-build": true }
```

Order in `build-phases` is execution order. `name` is required and should be unique within the target. Declare `output-paths` if the script produces files; otherwise set `"run-on-every-build": true`, or Xcode warns on every build that the script has no outputs. Add `"scope": "install"` for "run only when installing".

### Use an xcconfig file

Reference the file in `files`, then attach it by name:
```jsonc
"files": [ { "path": "Config/Shared.xcconfig" } ],
"configurations": [ { "name": "Debug", "file": "Shared.xcconfig" }, { "name": "Release", "file": "Shared.xcconfig" } ],
```
For a target, use `"specialized-configurations"` with the same shape. Configuration names must match the project's `configurations`.

## Reference

[references/format.md](references/format.md) — every known key, value, and path base (`<PRODUCTS>`, `<SDK>`, `<DEVELOPER>`, `<PROJECT>`), including dependencies on other projects, build rules, variant/version groups, file encodings, and build-file attributes. Read it before using a key that isn't in the recipes above.
