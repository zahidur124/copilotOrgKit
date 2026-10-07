# Corrections

date | symptom | command | output
2026-10-07 | The kit was built to push AGENTS.md and the deny hook into every org repo; the owner wanted opt-in files each developer installs on their own machine. The Goal in docs/spec.md was never filled, so nothing caught it. | grep -n 'Copies `templates/` into every repo' kit/README.md | 10:\| `scripts/sync.sh` \| Copies `templates/` into every repo in the org and opens a PR where they differ. \|
