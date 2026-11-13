#!/usr/bin/env python3
"""Install the kit into one repository's .github folder. You decide whether to commit the files.

The rules go in .github/instructions/kit.instructions.md, not AGENTS.md, so the repo's own AGENTS.md is never
touched. The hook, agents and skills go in .github/hooks/, .github/agents/ and .github/skills/.
"""
import os
import sys
from pathlib import Path

import installer as kit

EXAMPLES = """examples:
  python install-repo.py                          asks which repo, agents and skills, then installs
  python install-repo.py ~/code/my-service        installs into that repo, asking about agents and skills
  python install-repo.py ~/code/my-service --yes  installs everything there without asking
  python install-repo.py . --update --yes         brings an earlier install in this repo up to date"""


def git_root(start):
    for folder in [start, *start.parents]:
        if (folder / ".git").exists():
            return folder
    return None


def as_path(text):
    """Read a typed or drag-and-dropped folder path: strip quotes, unescape spaces, expand ~."""
    text = text.strip().strip("\"'")
    if os.name != "nt":
        text = text.replace("\\ ", " ")
    return Path(text).expanduser().resolve()


def ask_repo(guess, kit_repo):
    prompt = f"Which repository? Enter for {guess}, or type or drag in its folder: " if guess \
        else "Which repository? Type or drag in its folder: "
    while True:
        answer = input(prompt).strip()
        if not answer and guess:
            return guess
        if not answer:
            continue
        folder = as_path(answer)
        if not folder.is_dir():
            print(f"{folder} is not a folder.")
            continue
        root = git_root(folder)
        if root is None:
            print(f"{folder} is not in a git repository. Copilot reads .github/ only at a repository's root.")
            if kit.ask_yes_no("Install there anyway?", False):
                return folder
            continue
        if root == kit_repo:
            print("That is the kit's own repository. Pick the repository you want to use Copilot in.")
            continue
        if root != folder:
            if kit.ask_yes_no(f"{folder} is inside the repository {root}. Install at {root}?", True):
                return root
            continue
        return folder


def main():
    parser = kit.make_parser("Install the Copilot kit into one repository's .github folder.", EXAMPLES)
    parser.add_argument("dir", nargs="?", help="the repository's root folder (default: the repository you are in)")
    args = parser.parse_args()
    interactive = kit.is_interactive(args)
    kit_repo = git_root(kit.KIT)
    here = git_root(Path.cwd())
    guess = here if here and here != kit_repo else None

    if args.dir:
        dest = as_path(args.dir)
        if not dest.is_dir():
            parser.error(f"{dest} is not a folder")
        if not (dest / ".git").exists():
            print(f"warning: {dest} is not a git repository root; Copilot reads .github/hooks/ only at the root", file=sys.stderr)
    elif interactive:
        print("Copilot kit: install into one repository.")
        dest = ask_repo(guess, kit_repo)
    elif guess:
        dest = guess
    else:
        parser.error("give the repository's folder; the current folder is not inside a repository other than the kit's")

    rules = dest / ".github" / "instructions" / "kit.instructions.md"
    old = dest / "AGENTS.md"
    if old.exists() and old.read_bytes().startswith(kit.RULES.read_bytes().splitlines(keepends=True)[0]):
        print(f"warning: {old} looks like the kit's rules from an earlier install; they now live in {rules.relative_to(dest)}. "
              "Delete AGENTS.md unless you added your own rules to it, or Copilot reads the rules twice.", file=sys.stderr)

    agent_names, skill_names = kit.choose_agents_and_skills(args, interactive, parser)
    files = kit.file_list(rules, kit.REPO_RULES_HEADER, dest / ".github", agent_names, skill_names)
    kit.install(files, dest, args, interactive,
                "Nothing was committed: `git status` in the repository shows the new files; commit them if your team should have them.")


if __name__ == "__main__":
    kit.run(main)
