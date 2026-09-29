#!/usr/bin/env bash
# Copy templates/ into every repo in $ORG. Where a repo differs, push a branch and open a PR.
# The branch name carries a hash of templates/, so a rerun skips repos that already have that PR.
set -euo pipefail
kit=$(cd "$(dirname "$0")/.." && pwd)
hash=$(cd "$kit/templates" && find . -type f | sort | xargs cat | shasum | cut -c1-8)
branch="org-kit-sync-$hash"
work=$(mktemp -d)
for repo in $(gh repo list "$ORG" --no-archived --limit 1000 --json name -q '.[].name'); do
  [ "$repo" = ".github-private" ] && continue
  dir="$work/$repo"
  gh repo clone "$ORG/$repo" "$dir" -- --depth 1 -q
  if git -C "$dir" ls-remote --exit-code --heads origin "$branch" >/dev/null; then
    echo "skip $repo: $branch already open"; continue
  fi
  cp -R "$kit/templates/." "$dir/"
  if [ -z "$(git -C "$dir" status --porcelain)" ]; then
    echo "skip $repo: up to date"; continue
  fi
  git -C "$dir" checkout -q -b "$branch"
  git -C "$dir" add -A
  git -C "$dir" commit -qm "Sync org Copilot files from .github-private ($hash)"
  git -C "$dir" push -q origin "$branch"
  (cd "$dir" && gh pr create --head "$branch" \
    --title "Sync org Copilot files ($hash)" \
    --body "Automated copy of AGENTS.md and .github/hooks/org-deny.json from the org's .github-private repo. Edit them there, not here.")
  echo "PR opened in $repo"
done
