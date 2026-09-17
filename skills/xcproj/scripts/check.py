#!/usr/bin/env python3
"""Validate an Xcode JSON project (project.xcproj).

Usage: check.py path/to/App.xcodeproj [--list]

1. Runs `xcrun xcprojformatter` — fails on malformed JSON or invalid values.
2. Compares keys before/after formatting. Xcode silently drops unknown keys,
   so any key that disappears is a typo, a misplaced key, or a default value.
3. With --list, runs `xcodebuild -list` to make sure Xcode can load the project
   (catches unresolved target/phase names).
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def parse_jsonc(text):
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\":
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        elif text.startswith("/*", i):
            i = text.index("*/", i) + 2
            continue
        out.append(ch)
        i += 1
    return json.loads(re.sub(r",(\s*[\]}])", r"\1", "".join(out)))


def load(text, label):
    try:
        return parse_jsonc(text)
    except (json.JSONDecodeError, ValueError, IndexError) as error:
        print(f"SKIP key check: {label} uses JSON5 syntax this script can't parse ({error})")
        print("     Xcode accepts it; run `xcrun xcprojformatter --update` to rewrite as plain JSON, then re-run.")
        return None


def key_paths(node, path=""):
    """Yield paths of object keys, identifying array items by name/path/kind when possible."""
    if isinstance(node, dict):
        for key, value in node.items():
            p = f"{path}/{key}"
            yield p, value
            yield from key_paths(value, p)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            label = str(index)
            if isinstance(item, dict):
                ident = item.get("name") or item.get("path") or item.get("product-name") or item.get("target") or item.get("build-phase")
                if isinstance(ident, str):
                    label = ident
            yield from key_paths(item, f"{path}[{label}]")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    project = Path(args[0])
    if project.name == "project.xcproj":
        project = project.parent
    source = project / "project.xcproj"
    if not source.exists():
        sys.exit(f"error: {source} not found (plist projects use project.pbxproj; convert in Xcode's File inspector)")

    result = subprocess.run(
        ["xcrun", "xcprojformatter", "--input", str(project)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("FAIL xcprojformatter")
        print((result.stderr or result.stdout).strip())
        sys.exit(1)

    before = load(source.read_text(), "project.xcproj")
    after = load(result.stdout, "formatter output")
    if before is None or after is None:
        sys.exit(1)
    after_paths = {p for p, _ in key_paths(after)}
    dropped = [(p, v) for p, v in key_paths(before) if p not in after_paths]
    # Report only the outermost dropped key of each subtree.
    reported = []
    for p, v in dropped:
        if not any(p.startswith(r + "/") or p.startswith(r + "[") for r, _ in reported):
            reported.append((p, v))

    status = 0
    if reported:
        print("WARN keys dropped by Xcode (typo, wrong location, or default value):")
        for p, v in reported:
            print(f"  {p} = {json.dumps(v)[:80]}")
        status = 1
    else:
        print("OK   xcprojformatter: no keys dropped")

    if "--list" in sys.argv:
        listing = subprocess.run(
            ["xcodebuild", "-list", "-project", str(project)],
            capture_output=True, text=True,
        )
        text = listing.stdout + listing.stderr
        if "Unable to read project" in text:
            print("FAIL xcodebuild -list")
            print("\n".join(l for l in text.splitlines() if l.strip() and "xcresult" not in l)[:2000])
            status = 1
        else:
            print("OK   xcodebuild -list")

    sys.exit(status)


if __name__ == "__main__":
    main()
