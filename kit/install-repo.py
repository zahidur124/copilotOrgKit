#!/usr/bin/env python3
"""Set up one repository for Copilot: the safety hook, the agents and skills it uses, and its own AGENTS.md.
You decide whether to commit the files.

The hook, agents and skills go in .github/hooks/, .github/agents/ and .github/skills/. AGENTS.md is the kit's
project template with <placeholders>, written only when the repo has no AGENTS.md; the setup-project skill fills
it in. The kit's general working rules are not installed here: each developer gets them from install-user.py.
"""
import os
import re
import sys
from pathlib import Path

import installer as kit

TEMPLATE_TITLE = "# <project name>"

EXAMPLES = """examples:
  python install-repo.py                          asks which repo, agents and skills, then installs
  python install-repo.py ~/code/my-service        installs into that repo, asking about agents and skills
  python install-repo.py ~/code/my-service --yes  installs everything there without asking
  python install-repo.py . --update --yes         brings an earlier install in this repo up to date"""


def project_agents_md(agent_names):
    """The project template, with its Delegation section holding only the job lines for the agents being installed,
    or without that section when no agent is installed. A job line ends with the agent's name in backticks."""
    out, section = [], None
    for line in kit.PROJECT_TEMPLATE.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("## "):
            section = line.strip()
        if section == "## Delegation":
            if not agent_names:
                continue
            agent = re.search(r"`([\w-]+)`\.?\s*$", line)
            if line.startswith("  - ") and agent and agent.group(1) not in agent_names:
                continue
        out.append(line)
    return ("".join(out).rstrip("\n") + "\n").encode("utf-8")


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

    # Earlier versions of this script put the kit's general rules in the repo; they now come from install-user.py.
    general_rules_line = kit.RULES.read_bytes().splitlines(keepends=True)[0]
    for old in (dest / ".github" / "instructions" / "kit.instructions.md", dest / "AGENTS.md"):
        if old.exists() and general_rules_line in old.read_bytes().splitlines(keepends=True)[:5]:
            print(f"warning: {old.relative_to(dest)} holds the kit's general working rules from an earlier install. Those now come "
                  "from each developer's install-user.py, so delete it unless you added your own rules, or Copilot reads them twice."
                  + (" Then run this again to get the project template." if old.name == "AGENTS.md" else ""), file=sys.stderr)

    agents_md = dest / "AGENTS.md"
    if agents_md.exists() and agents_md.read_text(encoding="utf-8").startswith(TEMPLATE_TITLE):
        print("AGENTS.md is still the unfilled project template; ask Copilot to \"set up this repo for Copilot\" to fill it in.")
    elif agents_md.exists():
        print("AGENTS.md already exists and is left as it is; the setup-project skill can propose lines to add, "
              "such as Delegation lines for the agents installed here.")

    agent_names, skill_names = kit.choose_agents_and_skills(args, interactive, parser)
    extra = [(kit.HOOK, dest / ".github" / "hooks" / "deny.json")]
    if not agents_md.exists():
        extra.append((project_agents_md(agent_names), agents_md))
    files = kit.file_list(extra, dest / ".github", agent_names, skill_names)
    fill_in = ("Ask Copilot in the repository to \"set up this repo for Copilot\" so the setup-project skill fills in AGENTS.md's "
               "<placeholders>. " if not agents_md.exists() and "setup-project" in skill_names else
               "Fill in the <placeholders> in AGENTS.md before using Copilot there. " if not agents_md.exists() else "")
    kit.install(files, dest, args, interactive,
                fill_in + "Nothing was committed: `git status` in the repository shows the new files; "
                "commit them if your team should have them.")


if __name__ == "__main__":
    kit.run(main)
