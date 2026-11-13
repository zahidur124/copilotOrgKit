#!/usr/bin/env python3
"""Set up one repository for Copilot: the safety hook, the agents it uses, the skills and rules files of the packs
it uses, and its own AGENTS.md. You decide whether to commit the files.

The hook, agents, skills and rules files go in .github/hooks/, .github/agents/, .github/skills/ and
.github/instructions/. The packs suggested are the ones for the stacks whose build files are in the repo. AGENTS.md is the kit's
project template with <placeholders>, written when the repo has no AGENTS.md; the setup-project skill fills it
in. Its "Agents in this repo" section names the job of each kit agent in .github/agents/; when AGENTS.md
already exists, the script asks whether to merge (update only that section) or overwrite it with the template. The kit's general working rules are not
installed here: each developer gets them from install-user.py.
"""
import fnmatch
import os
import sys
from pathlib import Path

import installer as kit

TEMPLATE_TITLE = "# <project name>"
AGENTS_HEADING = "## Agents in this repo"
# Build files that show a repo's stack, and the pack each one suggests. They are looked for at the root and up to
# two folders down, skipping SKIP_DIRS and hidden folders such as .git and .dart_tool.
STACK_FILES = [
    ("pom.xml", "java"), ("build.gradle", "java"), ("build.gradle.kts", "java"),
    ("package.json", "node"),
    ("build.sbt", "scala"),
    ("pyproject.toml", "python"), ("requirements*.txt", "python"), ("setup.py", "python"),
    ("pubspec.yaml", "flutter"),
]
SKIP_DIRS = {"node_modules", "build", "target", "dist", "out", "venv", "env", "__pycache__", "site-packages", "vendor", "Pods"}
FLUTTER_PLATFORM_DIRS = {"android", "ios", "macos", "linux", "windows", "web"}
ALWAYS_SUGGESTED =["documents", "planning"]

EXAMPLES = """examples:
  python install-repo.py                          asks which repo, agents and packs, then installs
  python install-repo.py ~/code/my-service        installs into that repo, asking about agents and packs
  python install-repo.py ~/code/my-service --yes  installs all agents and the suggested packs there without asking
  python install-repo.py . --packs java,documents --yes
  python install-repo.py . --packs scala --skills csv-analysis --yes   the scala pack plus one more skill
  python install-repo.py . --skills build-and-test --yes               only that skill (no packs), and all agents
  python install-repo.py . --update --yes         brings an earlier install in this repo up to date"""


def detect_stacks(root):
    """Return {pack name: [build files found, relative to root]} for the stacks whose build files are in the repo."""
    found = {}

    def walk(folder, depth):
        try:
            entries = sorted(os.scandir(folder), key=lambda e: e.name)
        except OSError:
            return
        # A Flutter app's platform folders hold Gradle and other build files of its own; they are not a Java service.
        skip = SKIP_DIRS | (FLUTTER_PLATFORM_DIRS if any(e.name == "pubspec.yaml" for e in entries) else set())
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    if depth < 2 and not entry.name.startswith(".") and entry.name not in skip:
                        walk(entry.path, depth + 1)
                    continue
            except OSError:
                continue
            for pattern, pack in STACK_FILES:
                if fnmatch.fnmatchcase(entry.name, pattern):
                    found.setdefault(pack, []).append(Path(entry.path).relative_to(root).as_posix())

    walk(root, 0)
    return found


def suggest_packs(root):
    """Return (suggested packs, a note saying what was found): code, documents, planning and the detected stacks'
    packs, or only documents and planning when no stack is found."""
    found = detect_stacks(root)
    stacks = [p[0] for p in kit.PACKS if p[0] in found]
    if not stacks:
        return ALWAYS_SUGGESTED, ("No build files for Java, Node, Scala, Python or Flutter were found, so the suggestion "
                                  "leaves out the code pack.")
    shown = []
    for pack in stacks:
        files = found[pack]
        shown.append(f"{pack} ({', '.join(files[:3])}{f', and {len(files) - 3} more' if len(files) > 3 else ''})")
    return ["code"] + stacks + ALWAYS_SUGGESTED, "Build files found: " + "; ".join(shown) + "."



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

    agent_names = kit.choose("agent", args.agents, interactive, parser)
    suggested, found_note = suggest_packs(dest)
    if not interactive and args.packs is None and args.skills is None:
        print(found_note)
    skill_names, rule_names = kit.choose_packs(args, interactive, parser, suggested,
                                               ["A pack's rules files go in .github/instructions/ and load for matching files.",
                                                found_note], with_rules=True)
    content, plan = kit.rules_file(agents_md, kit.PROJECT_TEMPLATE.read_text(encoding="utf-8"), AGENTS_HEADING,
                                   kit.agents_after_install(dest / ".github" / "agents", agent_names), "", args, interactive)
    extra = [(kit.HOOK, dest / ".github" / "hooks" / "deny.json"), (content, agents_md)]
    files = kit.file_list(extra, dest / ".github", agent_names, skill_names, rule_names)
    from_template = not agents_md.exists() or (plan or "").startswith("overwrite")
    fill_in = ("Ask Copilot in the repository to \"set up this repo for Copilot\" so the setup-project skill fills in AGENTS.md's "
               "<placeholders>. " if from_template and "setup-project" in skill_names else
               "Fill in the <placeholders> in AGENTS.md before using Copilot there. " if from_template else "")
    kit.install(files, dest, args, interactive,
                fill_in + "Nothing was committed: `git status` in the repository shows the new files; "
                "commit them if your team should have them.", {agents_md: plan} if plan else None)


if __name__ == "__main__":
    kit.run(main)
