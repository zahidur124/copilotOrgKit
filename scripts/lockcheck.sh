#!/usr/bin/env bash
# Fails when a locked test changed, or when tests.lock changed outside a `wf red` commit
# (subject "red: ...", touching only tests/, tests.lock and features.json).
# Usage: scripts/lockcheck.sh [commit before this push]
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
sum() { if command -v sha256sum >/dev/null; then sha256sum "$@"; else shasum -a 256 "$@"; fi; }
if [ -s tests.lock ] && ! sum -c --quiet tests.lock; then
  echo "FAIL: a locked test differs from tests.lock"; fail=1
fi
before="${1:-}"
if [ -z "$before" ] || ! git cat-file -e "$before^{commit}" 2>/dev/null; then
  before=$(git merge-base HEAD origin/main 2>/dev/null || true)
fi
range="HEAD"; [ -n "$before" ] && [ "$before" != "$(git rev-parse HEAD)" ] && range="$before..HEAD"
[ -n "$before" ] && [ "$before" = "$(git rev-parse HEAD)" ] && range=""
for c in ${range:+$(git rev-list $range)}; do
  files=$(git diff-tree --root --no-commit-id --name-only -r "$c")
  echo "$files" | grep -qx 'tests.lock' || continue
  subject=$(git log -1 --format=%s "$c")
  other=$(echo "$files" | grep -vE '^(tests/|tests\.lock$|features\.json$)' | tr '\n' ' ')
  case "$subject" in red:*) ;; *) echo "FAIL: ${c:0:9} changes tests.lock but is not a red commit: $subject"; fail=1;; esac
  [ -z "$other" ] || { echo "FAIL: ${c:0:9} changes tests.lock together with code: $other"; fail=1; }
done
[ $fail -eq 0 ] && echo "PASS: locked tests unchanged"
exit $fail
