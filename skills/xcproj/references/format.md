# `.xcproj` format — reverse-engineered reference

**Unofficial.** Xcode 27.2 (27B5019j). No public spec exists. Sources:
- Swift model `XcodeProject.XCSchema` in `DevToolsCore.framework` (field and enum names)
- real plist → JSON conversions via Xcode UI on sample projects covering targets, packages, scripts, rules, localizations, folders, cross-project refs
- probing with `xcprojformatter` (validates + canonicalizes)

Legend: ✅ seen in Xcode output · 🧪 accepted & kept by formatter · 📦 only in binary

## Syntax
- `Demo.xcodeproj/project.xcproj` replaces `project.pbxproj` (having both = error)
- JSON superset: trailing commas, `//` and `/* */` comments accepted (formatter strips comments)
- **unknown keys silently dropped** — typo = lost setting. Run formatter and diff to catch
- IDs (`"id"`, 24 hex) needed only on targets and product file refs; everything else addressed by name/path
- defaults omitted (`false`, empty arrays, `"always"` scope …)

## Tooling
```sh
xcrun xcprojformatter --update X.xcodeproj    # canonicalize in place
xcrun xcprojformatter --input X.xcodeproj     # print canonical → diff to validate
```
Errors carry JSON path: `Missing required value for key "id" at "/targets[1]"`, `Unexpected value "zzz"`, `Invalid path base: "ZZZ"`.
Conversion plist→JSON: only Xcode UI (File inspector → Project Format).

## Root (`XCSchema.Project`)
| key | type | notes |
|---|---|---|
| `organization` ✅ | string | |
| `class-prefix` ✅ | string | |
| `build-independent-targets-in-parallel` ✅ | bool | default true |
| `default-configuration` ✅ | string | |
| `configurations` ✅ | [string \| {name, file}] | `file` = xcconfig path in group tree |
| `localizations` ✅ | {development, supported[]} | |
| `packages` ✅ | [Package] | |
| `imported-products` ✅ | [RemoteProduct] | products from referenced projects |
| `files` ✅ | [Reference] | main group children |
| `targets` ✅ | [Target] | |
| `build-settings` ✅ | {KEY: string} | per-config: `"KEY[config=Debug]"` |
| `products-group` ✅ | name path | omitted when `Products` |
| `last-upgrade`, `last-swift-update`, `last-swift-migration` ✅ | `"27.0"` | |
| `required-capabilities` 📦 | [string] | unknown values dropped |
| `root-group-debug-id`, `configuration-list-debug-id` 📦 | id | debug-only (`PBXProject.EncodeDebugIDs`) |

## Reference (`files`, `children`)
`kind`: `file-reference` (default, omitted) · `group` · `folder` · `variant-group` · `version-group` 🧪

**Paths**: relative to group; bases `<PRODUCTS>/`, `<SDK>/`, `<DEVELOPER>/`, `<PROJECT>/` 🧪; absolute `/…` ✅; `name` only when differs from last path component.

### file-reference
```jsonc
{ "path": "crlf.txt", "type": "text", "index": false, "id": "…",
  "encoding": "unicode", "line-ending": "carriage-return-line-feed",
  "target-membership": [ "App/resources", { "build-phase": "App/frameworks", "is-weak": true } ] }
```
- `type` = explicitFileType; `index` = includeInIndex; `expected-signature` 📦
- `encoding` 🧪: `utf8 utf16 utf16-big-endian utf16-little-endian utf32 utf32-big-endian utf32-little-endian ascii non-lossy-ascii unicode nextstep symbol macos-roman iso-latin-1 iso-latin-2 japanese-euc shift-jis iso-2022-jp windows-code-page-1250…1254`
- `line-ending` 🧪: `line-feed carriage-return carriage-return-line-feed preserve`

### group / variant-group / version-group
```jsonc
{ "kind": "group", "path": "Legacy", "name": "…", "children": [ … ] }
{ "kind": "variant-group", "name": "Legacy.strings", "target-membership": ["App/resources"],
  "children": [ { "path": "en.lproj/Legacy.strings" } ] }
{ "kind": "version-group", "path": "Model.xcdatamodeld", "current-version": "Model2.xcdatamodel",
  "type": "wrapper.xcdatamodel", "children": [ … ] }
```

### folder (synchronized)
```jsonc
{ "kind": "folder", "path": "Lib",
  "target-membership": [ "Lib" ],
  "file-types": { "special.dat": "sourcecode.swift" },
  "opaque-folders": [ "Bundle.pack" ],
  "membership-exceptions": [
    { "target": "Lib",
      "exclusions": [ "Excluded.txt" ],          // or "inclusions" (not both)
      "public-headers": [ "a.h" ], "private-headers": [ "b.h" ],
      "compiler-flags": { "Lib.c": "-Wall" },
      "platforms": { "Lib.c": [ "ios", "macos" ] },
      "attributes": { "Lib.c": { "code-generation": "skip" } },
      "asset-tags": { "big.bin": [ "tagA" ] } },
    { "build-phase": "Lib/compile-sources", "exclusions": [ "Other.swift" ] }
  ] }
```

## Build files → `target-membership`
No PBXBuildFile objects. File/group lists its phases:
- string `"Target/phase"` · `"Target/copy/<phase name>"` · `"Target/script/<name>"`
- object `{ "build-phase": "…", …attrs }`

Attrs (`BuildFileAttributes` / `BuildFileProperties`):
| key | values |
|---|---|
| `arguments` ✅ | compiler flags string |
| `platforms` ✅ | [platform] |
| `asset-tags` ✅ | [string] |
| `is-weak` ✅ | bool |
| `code-sign-on-copy` ✅ | bool |
| `header-preservation` ✅ | `keep` · `remove-on-copy` |
| `header-role` 🧪 | `public` · `private` |
| `code-generation` ✅ | `default` · `skip` |
| `code-generation-visibility` 🧪 | `public` · `private` · `project` |
| `mach-interface-generation` 🧪 | `client` · `server` · `both` |
| `decompress` 📦 | bool |

## Target
```jsonc
{ "name": "App", "id": "…",
  "kind": "native",                      // default; aggregate · external-build-system
  "product": "Products/App.app",         // name path in group tree
  "product-type": "application",         // com.apple.product-type.* prefix stripped
  // "full-product-type": "com.acme.product-type.x"   🧪 non-Apple ids
  "test-host-target": "App",
  "dependencies": [ … ],
  "build-phases": [ … ],
  "build-rules": [ … ],
  "specialized-configurations": [ { "name": "Debug", "file": "Target.xcconfig" } ],
  "package-product-members": [ … ],
  "build-settings": { … },
  "legacy-provisioning-style": "manual", // automatic · manual
  "legacy-team-id": "ABCDE12345",
  "last-swift-migration": "26.0" }
```
external-build-system extra ✅: `build-tool-path`, `build-tool-arguments`, `build-tool-working-directory`, `pass-build-settings-in-environment` (default true).

### dependencies ✅
```jsonc
"Kit"                                                       // local target
{ "target": "Lib", "platforms": [ "ios" ] }                  // local + filter
{ "kind": "remoteTarget", "project": "Demo.xcodeproj", "target": "Demo", "target-id": "AA…06" }
{ "kind": "package", "package": "swift-log", "product-name": "Logging" }
```
`kind` 🧪: `localTarget` · `remoteTarget` · `package` (camelCase — exception to kebab-case)

### build-phases
Plain strings 🧪: `compile-sources` `frameworks` `resources` `headers` `rez` `java-archive`.
Objects (`kind` 🧪: + `copy` `script` `apple-script`), `name` required:
```jsonc
{ "kind": "copy", "name": "Embed Frameworks",
  "bundle-base-path": "frameworks-directory", "relative-path": "Sub/Dir", "scope": "install" }
{ "kind": "script", "name": "Lint", "shell": "/bin/sh", "script": "…",
  "input-paths": [], "input-file-list-paths": [], "output-paths": [], "output-file-list-paths": [],
  "dependency-file": "…", "run-on-every-build": true, "log-environment-variables": true,
  "scope": "install" }                   // scope: always (default) · install
{ "kind": "apple-script", "name": "…", "context-name": "…", "is-shared-context": true }   📦
```
`bundle-base-path` 🧪: `root build-products-directory contents-directory executables-directory resources-directory frameworks-directory shared-frameworks-directory shared-support-directory plugins-directory headers-directory private-headers-directory java-directory apple-scripts-directory info-plist-file package-info-file main-executable-file shallow-main-executable-file`. Omitted → absolute path in `relative-path`.

### build-rules ✅
```jsonc
{ "name": "Custom Files", "processor": "com.apple.compilers.proxy.script",
  "file-type": "pattern.proxy", "file-patterns": "*.custom",
  "input-files": [], "input-file-lists": [], "output-files": [], "output-file-lists": [],
  "output-files-compiler-flags": [], "dependency-file": "…",
  "run-once-per-architecture": true, "script": "…" }
```

### package-product-members ✅
```jsonc
{ "package": "swift-algorithms", "product-name": "Algorithms",
  "product-type": "build-tool-plugin",   // other (default) · build-tool-plugin
  "build-phase": { "build-phase": "frameworks", "platforms": [ "ios" ] } }
```
Local packages: `package` omitted.

## Packages ✅
```jsonc
{ "kind": "local", "path": "LocalPkg" }
{ "kind": "remote", "repository": "https://github.com/apple/swift-log",
  "version": { "up-to-next-major-version": "1.2.0" } }
```
`version` variants: `version` (exact) · `branch` · `revision` · `up-to-next-minor-version` · `up-to-next-major-version` · `version-range: "1.0.0..<2.0.0"` (or `version-range-min`/`version-range-max` 📦). `traits` [string] 📦.

## Imported products ✅
```jsonc
{ "name": "Demo.app", "project": "Demo.xcodeproj", "target": "Demo",
  "product-id": "AA…01", "type": "wrapper.application",
  "target-membership": [ "Kitchen/copy/Copy Demo" ] }
```

## Not preserved on conversion (observed)
- `lastKnownFileType` (inferred), `usesTabs`/`indentWidth`/`tabWidth`
- `CreatedOnToolsVersion`, `hasScannedForEncodings`, `knownRegions` order
- script phase default name when missing → `"Run Script"`

## Open
- custom source trees (`sourceRoot(String)` base) syntax — `<NAME>` rejected
- valid `required-capabilities` values
- `Strictly Validate` decoding option effect
