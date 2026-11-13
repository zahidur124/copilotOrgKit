"""Shared code for install-user.py and install-repo.py. Run one of those, not this file.

Each script asks what it needs when it runs in a terminal: which agents and skills, whether to replace
files that differ from the kit, and a last go-ahead after showing what it will do. A flag answers a
question in advance, so that question is not asked. Without a terminal (a pipe, CI) or with --yes,
nothing is asked: every agent and skill is installed and files that differ are skipped unless --update.

Runs on Windows, macOS and Linux with Python 3.8 or later; needs nothing outside the standard library.
"""
import argparse
import shutil
import sys
import textwrap
from pathlib import Path

KIT = Path(__file__).resolve().parent
RULES = KIT / "templates" / "AGENTS.md"
HOOK = KIT / "templates" / ".github" / "hooks" / "deny.json"
# An .instructions.md file applies only to the files its applyTo matches; "**" makes the kit's rules apply everywhere.
REPO_RULES_HEADER = b'---\napplyTo: "**"\n---\n\n'
# Kit files a skill copies into a project. They are installed inside the skill's own folder, so the skill finds
# them wherever it is installed and does not depend on where the kit was cloned.
SKILL_FILES = {
    "setup-project": [
        (KIT / "templates" / "project" / "AGENTS.md", "templates/project-AGENTS.md"),
        (KIT / "templates" / "research" / "AGENTS.md", "templates/research-AGENTS.md"),
    ] + [(f, f"agents/{f.name}") for f in sorted((KIT / "agents").glob("*.agent.md"))],
}


def _description(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip("\"'").replace('\\"', '"')
    return ""


def kit_items(kind):
    """Return [(name, description)] for every agent or skill in the kit."""
    if kind == "agent":
        return [(f.name[: -len(".agent.md")], _description(f)) for f in sorted((KIT / "agents").glob("*.agent.md"))]
    return [(f.parent.name, _description(f)) for f in sorted((KIT / "skills").glob("*/SKILL.md"))]


def make_parser(description, usage_examples):
    parser = argparse.ArgumentParser(description=description, epilog=usage_examples,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    agents = ", ".join(n for n, _ in kit_items("agent"))
    skills = ", ".join(n for n, _ in kit_items("skill"))
    parser.add_argument("--agents", metavar="NAMES", help=f"comma-separated agents to install, or all, or none. Kit agents: {agents}")
    parser.add_argument("--skills", metavar="NAMES", help=f"comma-separated skills to install, or all, or none. Kit skills: {skills}")
    parser.add_argument("--update", action="store_true", help="replace installed files that differ from the kit, keeping each old one as <name>.bak")
    parser.add_argument("--yes", "-y", action="store_true", help="ask nothing: use the flags given and install everything else")
    return parser


def is_interactive(args):
    return not args.yes and sys.stdin.isatty()


def ask_yes_no(question, default):
    hint = "[Y/n]" if default else "[y/N]"
    while True:
        answer = input(f"{question} {hint} ").strip().lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer y or n.")


def _parse_names(text, names):
    """Turn 'all', 'none', '1,3' or 'worker,reader' into a list of names, or raise ValueError."""
    text = text.strip().lower()
    if text in ("", "all"):
        return list(names)
    if text == "none":
        return []
    chosen = []
    for part in (p.strip() for p in text.replace(" ", ",").split(",")):
        if not part:
            continue
        if part.isdigit() and 1 <= int(part) <= len(names):
            part = names[int(part) - 1]
        if part not in names:
            raise ValueError(part)
        if part not in chosen:
            chosen.append(part)
    return chosen


def choose(kind, flag_value, interactive, parser):
    """Return the agent or skill names to install, from the flag, a question, or all of them."""
    items = kit_items(kind)
    names = [n for n, _ in items]
    if flag_value is not None:
        try:
            return _parse_names(flag_value, names)
        except ValueError as bad:
            parser.error(f"unknown {kind}: {bad}; choose from {', '.join(names)}")
    if not interactive:
        return names
    width = min(shutil.get_terminal_size().columns, 120) - 1
    print(f"\n{kind.capitalize()}s in the kit:")
    for i, (name, desc) in enumerate(items, 1):
        # Two lines of each description, enough to tell the items apart.
        lines = textwrap.wrap(desc, width - 27, max_lines=2, placeholder=" ...") or [""]
        print(f"  {i:>2}. {name:<20} {lines[0]}")
        for more in lines[1:]:
            print(" " * 27 + more)
    while True:
        answer = input(f"Which {kind}s? Enter for all, numbers or names such as 1,3 for some, or none: ")
        try:
            chosen = _parse_names(answer, names)
        except ValueError as bad:
            print(f"There is no {kind} {bad}. Use the numbers 1 to {len(names)} or the names listed.")
            continue
        print(f"  {kind.capitalize()}s: {', '.join(chosen) if chosen else 'none'}")
        return chosen


def choose_agents_and_skills(args, interactive, parser):
    agent_names = choose("agent", args.agents, interactive, parser)
    if "worker" not in agent_names:
        print("note: the working rules hand work to the worker agent, which you are not installing", file=sys.stderr)
    skill_names = choose("skill", args.skills, interactive, parser)
    return agent_names, skill_names


def file_list(rules_dst, rules_header, base, agent_names, skill_names):
    """Return [(content bytes, destination)] for the rules, the hook, and the chosen agents and skills.
    base is the folder that holds hooks/, agents/ and skills/."""
    hooks, agents, skills = base / "hooks", base / "agents", base / "skills"
    files = [(rules_header + RULES.read_bytes(), rules_dst), (HOOK, hooks / "deny.json")]
    files += [(KIT / "agents" / f"{n}.agent.md", agents / f"{n}.agent.md") for n in agent_names]
    for n in skill_names:
        folder = KIT / "skills" / n
        files.append((folder / "SKILL.md", skills / n / "SKILL.md"))
        files += [(src, skills / n / rel) for src, rel in SKILL_FILES.get(n, [])]
        # Helper files that sit beside a skill's SKILL.md (scripts, examples) go with it.
        files += [(f, skills / n / f.relative_to(folder)) for f in sorted(folder.rglob("*"))
                  if f.is_file() and f.name not in ("SKILL.md", ".DS_Store") and "__pycache__" not in f.parts and f.suffix != ".pyc"]
    return [(c if isinstance(c, bytes) else c.read_bytes(), d) for c, d in files]


def install(files, dest, args, interactive, next_steps):
    """Show what will happen, ask to go ahead when interactive, then write the files."""
    def show(path):
        try:
            return str(path.relative_to(dest))
        except ValueError:
            return str(path)

    new = [(c, d) for c, d in files if not d.exists()]
    same = [(c, d) for c, d in files if d.exists() and d.read_bytes() == c]
    differ = [(c, d) for c, d in files if d.exists() and d.read_bytes() != c]

    print(f"\nInto {dest}:")
    print(f"  {len(new)} new file(s) to install")
    print(f"  {len(same)} file(s) already up to date")
    if differ:
        print(f"  {len(differ)} file(s) differ from the kit (changed by you, or from an older kit):")
        for _, d in differ:
            print(f"      {show(d)}")

    replace = args.update
    if differ and not replace and interactive:
        replace = ask_yes_no("Replace the files that differ? Each old file is kept beside it as <name>.bak.", False)
    if not new and not (differ and replace):
        print("\nNothing to install." + (" Run again with --update to replace the files that differ." if differ else ""))
        return
    if interactive and not ask_yes_no("Install now?", True):
        print("Nothing was installed.")
        return

    print()
    for content, dst in new:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(content)
        print(f"installed: {show(dst)}")
    for content, dst in differ:
        if replace:
            backup = dst.with_name(dst.name + ".bak")
            shutil.copyfile(dst, backup)
            dst.write_bytes(content)
            print(f"replaced:  {show(dst)} (old file kept as {backup.name})")
        else:
            print(f"skipped, differs from the kit: {show(dst)}")
    if differ and not replace:
        print(f"\n{len(differ)} file(s) differ from the kit and were left alone; run again with --update to replace them (the old ones are kept as .bak).")
    print("\nDone. " + next_steps)


def run(main):
    """Run a script's main(), turning Ctrl-C or a closed input into a plain message."""
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. Nothing more was installed.")
        sys.exit(1)
