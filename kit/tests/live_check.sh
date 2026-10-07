#!/usr/bin/env bash
# Run the real Copilot CLI against a throwaway repo holding this kit's files.
# Fails when a Copilot release stops loading the agents or honoring the hook.
set -uo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd)
repo=$(mktemp -d)
cd "$repo"
git init -q && echo one > f.txt && git add f.txt
git -c user.name=t -c user.email=t@t commit -qm init
"$kit/install.sh" repo . >/dev/null
echo two > f.txt
ask() { copilot -s --allow-all-tools --no-ask-user "$@" 2>&1; }
fails=0
check() { if [ "$2" = ok ]; then echo "PASS: $1"; else echo "FAIL: $1: $3"; fails=$((fails+1)); fi; }

out=$(ask -p 'Run exactly this shell command and show its output: git status --short')
[[ "$out" == *"f.txt"* ]] && check "allowed command runs" ok || check "allowed command runs" no "$out"

ask -p 'Run exactly this shell command once, do not try alternatives: git reset --hard' >/dev/null
[ "$(cat f.txt)" = two ] && check "hook blocks git reset --hard" ok || check "hook blocks git reset --hard" no "f.txt was reset"

out=$(ask --agent no-such-agent -p hi)
for a in builder reader verifier reviewer; do
  [[ "$out" =~ (^|[ ,])$a(,|$|[[:space:]]) ]] && check "agent $a loads" ok || check "agent $a loads" no "$out"
done

echo two > f.txt
out=$(ask --agent verifier -p 'Done when: `cat f.txt` prints `one`')
[[ "$out" == *FAIL* ]] && check "verifier reports FAIL on a wrong file" ok || check "verifier reports FAIL on a wrong file" no "$out"

exit $fails
