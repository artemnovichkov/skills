#!/usr/bin/env bash
# Blocks edits to test files while sdlc/.lock-tests exists.
#
# The bug-fix loop is: write the failing test, commit it, then make it pass
# without touching the test. This hook makes that order real. It does nothing
# unless the marker file is present, so ordinary test writing is unaffected.
#
# Toggle with: /sdlc:verify --lock-tests  /  /sdlc:verify --unlock-tests
set -euo pipefail

input="$(cat)"

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
marker="$project_dir/sdlc/.lock-tests"

# Not locked: stay out of the way.
[ -f "$marker" ] || exit 0

extract_file_path() {
  if command -v python3 > /dev/null 2>&1; then
    python3 -c 'import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
i = d.get("tool_input") or {}
print(i.get("file_path") or i.get("notebook_path") or "")' <<< "$input" 2>/dev/null || true
  else
    sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' <<< "$input" | head -1
  fi
}

file_path="$(extract_file_path)"
[ -n "$file_path" ] || exit 0

is_test_file() {
  local path="$1"
  case "$path" in
    */Tests/*|*/test/*|*/tests/*|*/__tests__/*|*/spec/*) return 0 ;;
    *Test.swift|*Tests.swift|*Spec.swift) return 0 ;;
    *_test.go|*_test.py|*_test.rb|*_test.rs) return 0 ;;
    */test_*.py) return 0 ;;
    *.test.js|*.test.ts|*.test.jsx|*.test.tsx) return 0 ;;
    *.spec.js|*.spec.ts|*.spec.jsx|*.spec.tsx) return 0 ;;
    *) return 1 ;;
  esac
}

if is_test_file "$file_path"; then
  cat >&2 <<EOF
Blocked: test files are locked while $marker exists.

You are in a bug-fix loop: the failing test is the specification. Make the
code satisfy it instead of changing the test.

If the test itself is genuinely wrong, stop and say so to the user rather
than editing around it. To lift the lock, they can run:

  /sdlc:verify --unlock-tests

Blocked path: $file_path
EOF
  exit 2
fi

exit 0
