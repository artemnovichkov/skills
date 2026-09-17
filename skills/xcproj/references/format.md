# `.xcproj` format reference

Source of truth: Apple's reference implementation [apple/xcode-project-format](https://github.com/apple/xcode-project-format) — Swift types under `XCSchema` (`Sources/Library/Schema`), [docs](https://swiftpackageindex.com/apple/xcode-project-format/documentation/XcodeProjectFormat). Type names below point there. Notes marked **Xcode** are observed Xcode 27.2 behavior, not part of the library.

## Syntax
- `App.xcodeproj/project.xcproj` replaces `project.pbxproj` (**Xcode**: having both = error)
- JSON5: comments, trailing commas, single quotes, unquoted keys. The formatter strips comments
- **Unknown keys are ignored** — typo = lost setting, no error
- Keys that aren't required and default to nothing also accept `null` (= absent)
- Arrays declared as sets (platforms, supported languages, asset tags, opaque folders, folder target membership…) must not contain duplicates
- Defaults are omitted on encode (`false`, `[]`, `"always"`, `"native"` …)
- IDs (`ObjectID`) are any string; by convention 24 uppercase hex chars. Required only on targets (and `imported-products`)

## Tooling
```sh
xcrun xcprojformatter --update X.xcodeproj    # canonicalize in place
xcrun xcprojformatter --input X.xcodeproj     # print canonical → diff to validate
```
Errors carry a JSON path: `Missing required value for key "id" at "/targets[1]"`, `Unexpected value "zzz"`, `Invalid path base: "ZZZ"`.
**Xcode**: plist → JSON conversion only in the UI (File inspector → Project Format).

## Shared value types

**Name path** (`NamePath`) — path through the group tree by reference names, e.g. `"Products/App.app"`. `.`/`..` are relative components. A name containing `/` (or literally `.`/`..`) needs the array form: `[ "Group", { "name": "a/b" } ]`.

**Group tree reference** (`GroupTreeReference`) — name path, or `"id:<ObjectID>"` when names are ambiguous. Used by `product`, `products-group`, `current-version`, `project`, configuration `file`.

**File path** (`FilePath`) — `path` key of references, default `""`:
| form | base |
|---|---|
| `Sources/a.swift` | parent group |
| `/abs/path` | absolute |
| `<PROJECT>/…` `<PRODUCTS>/…` `<SDK>/…` `<DEVELOPER>/…` | built-in |
| `<USER:SETTING>/…` | source tree named by a build setting (escape `>` and `\` inside as `\>`, `\\`) |
- relative/absolute paths escape `<` and `\` as `\<`, `\\`
- paths can't start with `~`; after a base, the path can't start with `/` or `~`

**Marketing version** — `"27.0"` or `"26.3.1"` (2–3 integers).

**Multiline text** — string, or array of lines (joined with `\n`). Used by script phases and build rules.

## Root (`Project`)
| key | type | notes |
|---|---|---|
| `required-capabilities` | [string] | decoding **fails** on any capability the tool doesn't know ("requires a newer version") — don't add |
| `id`, `root-group-debug-id`, `configuration-list-debug-id` | id | |
| `organization`, `class-prefix` | string | |
| `build-independent-targets-in-parallel` | bool | default `true` |
| `default-configuration` | string | **required** |
| `configurations` | [Configuration] | |
| `localizations` | `{development, supported[]}` | **required**; `supported` excludes `development` |
| `imported-products` | [RemoteProduct] | products of referenced projects |
| `packages` | [SwiftPackage] | |
| `files` | [Reference] | **required**; main group children |
| `targets` | [Target] | names must be unique |
| `build-settings` | {KEY: string \| [string]} | conditions as key suffix: `KEY[config=Debug]`, `KEY[sdk=iphoneos*]` |
| `products-group` | group tree ref \| null | default `"Products"`; **Xcode**: the group must exist in `files`, else `Invalid reference: "Products"` |
| `last-upgrade`, `last-swift-update`, `last-swift-migration` | marketing version | |

### Configuration
```jsonc
"Debug"                                                   // plain
{ "name": "Debug", "file": "Shared.xcconfig", "id": "…" } // xcconfig by group tree ref
{ "name": "Debug", "file": { "anchor": "Config", "relative-path": "Debug.xcconfig" } }  // file inside a synchronized folder
```

## Reference (`files`, `children`)
`kind`: `file-reference` (default, omitted) · `group` · `folder` · `variant-group` · `version-group`.
Common: `id`, `index` (includeInIndex), `path`.

### file-reference (`FileReference`)
```jsonc
{ "path": "crlf.txt", "type": "text", "index": false, "id": "…",
  "signature": "…", "encoding": "utf8", "line-ending": "carriage-return-line-feed",
  "target-membership": [ "App/resources", { "build-phase": "App/frameworks", "is-weak": true } ] }
```
- no `name` key — name is the last path component
- `type` = explicit file type (`sourcecode.swift`, `wrapper.framework` …)
- `encoding`: `utf8 utf16 utf16-big-endian utf16-little-endian utf32 utf32-big-endian utf32-little-endian ascii non-lossy-ascii unicode nextstep symbol macos-roman iso-latin-1 iso-latin-2 japanese-euc shift-jis iso-2022-jp windows-code-page-1250…1254`, or raw `String.Encoding` integer
- `line-ending`: `line-feed carriage-return carriage-return-line-feed preserve`

### group / variant-group / version-group
`name` only when it differs from the last path component.
```jsonc
{ "kind": "group", "path": "Legacy", "name": "Old Stuff", "children": [ … ] }
{ "kind": "variant-group", "name": "Legacy.strings", "target-membership": [ "App/resources" ],
  "children": [ { "path": "en.lproj/Legacy.strings" } ] }          // children: file references only
{ "kind": "version-group", "path": "Model.xcdatamodeld", "current-version": "Model2.xcdatamodel",
  "type": "wrapper.xcdatamodel", "target-membership": [ … ], "children": [ … ] }
```
Groups have no `target-membership`.

### folder (synchronized, `Folder`)
No `name` key.
```jsonc
{ "kind": "folder", "path": "Lib",
  "target-membership": [ "Lib" ],                  // target names
  "file-types": { "special.dat": "sourcecode.swift" },
  "opaque-folders": [ "Bundle.pack" ],
  "membership-exceptions": [
    { "target": "Lib",
      "exclusions": [ "Excluded.txt" ],            // or "inclusions", not both
      "public-headers": [ "a.h" ], "private-headers": [ "b.h" ],
      "compiler-flags": { "Lib.c": "-Wall" },
      "platforms": { "Lib.c": [ "ios", "macos" ] },
      "attributes": { "Lib.c": { "code-generation": "skip" } },
      "asset-tags": { "big.bin": [ "tagA" ] } },
    { "build-phase": "Lib/copy/Embed", "inclusions": [ "Tool" ] }   // map files into a specific phase
  ] }
```
- keys are paths relative to the folder
- target exception (`TargetExceptionSet`) wins if both `target` and `build-phase` are present
- build-phase exception (`BuildPhaseExceptionSet`) takes `inclusions`/`exclusions`, `platforms`, `attributes`, `asset-tags` — header and flag keys are ignored

## Build files → `target-membership`
No PBXBuildFile objects; the file lists its phases (`ProjectBuildFile`).

**Build phase reference** (`ProjectBuildPhaseReference`): `"Target/<kind>"` or `"Target/<kind>/<phase name>"`, `kind` is any build phase kind (`compile-sources`, `frameworks`, `copy`, `script` …). Use `"id:<phase id>"` when the name is ambiguous, or the array form `[ "Target", "copy", { "name": "a/b" } ]` when a name contains `/`.

- string: `"App/compile-sources"`
- object: `{ "build-phase": <ref>, "id": "…", …properties }` (array ref only allowed here)

Properties (`BuildFileProperties` + `BuildFileAttributes`):
| key | values |
|---|---|
| `arguments` | compiler flags string |
| `platforms` | [platform] |
| `asset-tags` | [string] |
| `is-weak` | bool |
| `code-sign-on-copy` | bool |
| `decompress` | bool |
| `header-preservation` | `keep` (default) · `remove-on-copy` |
| `header-role` | `public` · `private` |
| `code-generation` | `default` · `skip` |
| `code-generation-visibility` | `public` · `private` · `project` |
| `mach-interface-generation` | `client` · `server` · `both` |

## Target (`Target`)
```jsonc
{ "name": "App", "id": "…",                // both required
  "kind": "native",                        // default; aggregate · external-build-system
  "product": "Products/App.app",           // group tree ref
  "product-type": "application",           // com.apple.product-type.* with prefix stripped
  // "full-product-type": "com.acme.product-type.x"   ids outside com.apple.product-type.*; ignored if product-type is set
  "test-host-target": "App",
  "dependencies": [ … ],
  "build-phases": [ … ],
  "build-rules": [ … ],
  "specialized-configurations": [ { "name": "Debug", "file": "Target.xcconfig" } ],  // must have file or id
  "package-product-members": [ … ],
  "build-settings": { … },
  "legacy-provisioning-style": "manual",   // automatic · manual
  "legacy-team-id": "ABCDE12345",
  "last-swift-update": "26.0", "last-swift-migration": "26.0",
  "configuration-list-debug-id": "…" }
```
`external-build-system` (`ExternalBuildSystemTargetProperties`): `build-tool-path` (required), `build-tool-arguments` (default `""`), `build-tool-working-directory`, `pass-build-settings-in-environment` (default `true`).

### dependencies (`TargetDependency`)
```jsonc
"Kit"                                                                    // local target
{ "target": "Lib", "platforms": [ "ios" ] }                              // local + filter
{ "kind": "remoteTarget", "project": "Demo.xcodeproj", "target": "Demo", "target-id": "AA…06" }
{ "kind": "package", "package": "swift-log", "product-name": "Logging", "product-type": "other", "id": "…" }
```
`kind`: `localTarget` (default) · `remoteTarget` · `package` — camelCase, the exception to kebab-case. All accept `platforms`.

### build-phases (`BuildPhase`)
Plain strings: `compile-sources` `frameworks` `resources` `headers` `rez` `java-archive`.
Objects take `kind`, optional `name` and `id`:
```jsonc
{ "kind": "resources", "name": "Extra Resources" }
{ "kind": "copy", "name": "Embed Frameworks",
  "bundle-base-path": "frameworks-directory", "relative-path": "Sub/Dir", "scope": "install" }
{ "kind": "script", "name": "Lint",
  "shell": "/bin/sh", "script": "…",       // shell and script required; script may be an array of lines
  "input-paths": [], "input-file-list-paths": [], "output-paths": [], "output-file-list-paths": [],
  "dependency-file": "…", "run-on-every-build": true, "log-environment-variables": true,
  "scope": "install" }                     // always (default) · install
{ "kind": "apple-script", "name": "…", "context-name": "…", "is-shared-context": true }
```
`bundle-base-path`: `root build-products-directory contents-directory executables-directory resources-directory frameworks-directory shared-frameworks-directory shared-support-directory plugins-directory headers-directory private-headers-directory java-directory apple-scripts-directory info-plist-file package-info-file main-executable-file shallow-main-executable-file`. Omitted → `relative-path` is absolute.

### build-rules (`BuildRule`)
```jsonc
{ "name": "Custom Files", "id": "…",
  "processor": "com.apple.compilers.proxy.script",   // required
  "file-type": "pattern.proxy", "file-patterns": "*.custom",
  "input-files": [], "input-file-lists": [], "output-files": [], "output-file-lists": [],
  "output-files-compiler-flags": [], "dependency-file": "…",
  "run-once-per-architecture": true,       // default true
  "script": "…" }                          // string or array of lines
```

### package-product-members (`SwiftPackageProductTargetMember`)
```jsonc
{ "package": "swift-algorithms", "product-name": "Algorithms", "id": "…",
  "product-type": "build-tool-plugin",     // other (default) · build-tool-plugin
  "build-phase": { "build-phase": "frameworks", "platforms": [ "ios" ] } }
```
- `package` omitted for local packages
- `build-phase` is always an object; its ref has no target: `"<kind>[/<name>]"` or `"id:…"`

## Packages (`SwiftPackage`)
```jsonc
{ "kind": "local", "path": "LocalPkg", "traits": [ "Foo" ] }
{ "kind": "remote", "repository": "https://github.com/apple/swift-log",
  "version": { "up-to-next-major-version": "1.2.0" }, "traits": [ … ] }
```
`version` (`SwiftPackageVersionConstraint`), first present key wins: `revision` · `branch` · `version` (exact) · `up-to-next-minor-version` · `up-to-next-major-version` · `"version-range": "1.0.0..<2.0.0"` · `version-range-min` + `version-range-max` (used when bounds aren't plain numeric versions).

## Imported products (`RemoteProduct`)
```jsonc
{ "name": "Demo.app",                      // single-component path; otherwise "path": "sub/Demo.app"
  "project": "Demo.xcodeproj", "target": "Demo", "product-id": "AA…01",   // required
  "type": "wrapper.application",
  "target-membership": [ "Kitchen/copy/Copy Demo" ] }                    // required
```

## Xcode conversion notes (observed)
- not preserved: `lastKnownFileType` (inferred), `usesTabs`/`indentWidth`/`tabWidth`, `CreatedOnToolsVersion`, `hasScannedForEncodings`, `knownRegions` order
- script phase without a name converts to `"Run Script"`
