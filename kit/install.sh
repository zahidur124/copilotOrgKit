#!/usr/bin/env bash
# Copy this kit's agents, working rules and deny hook to where Copilot reads them.
#   ./install.sh user        into your Copilot config ($COPILOT_HOME or ~/.copilot); applies to every repo you open
#   ./install.sh repo [dir]  into one repo (default: the current directory); you decide whether to commit them
# A file that already exists is skipped, never overwritten.
set -euo pipefail
kit=$(cd "$(dirname "$0")" && pwd)
case "${1:-}" in
  user) dest=${COPILOT_HOME:-$HOME/.copilot}; rules=$dest/copilot-instructions.md; hooks=$dest/hooks; agents=$dest/agents ;;
  repo) dest=$(cd "${2:-.}" && pwd); rules=$dest/AGENTS.md; hooks=$dest/.github/hooks; agents=$dest/.github/agents ;;
  *) echo "usage: $0 user | repo [dir]" >&2; exit 2 ;;
esac
put() {
  if [ -e "$2" ]; then echo "skipped, already exists: $2"
  else mkdir -p "$(dirname "$2")" && cp "$1" "$2" && echo "installed: $2"; fi
}
put "$kit/templates/AGENTS.md" "$rules"
put "$kit/templates/.github/hooks/org-deny.json" "$hooks/org-deny.json"
for f in "$kit"/agents/*.agent.md; do put "$f" "$agents/$(basename "$f")"; done
