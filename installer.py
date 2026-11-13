"""Shared code for install-user.py and install-repo.py. Run one of those, not this file.

Each script asks what it needs when it runs in a terminal: which agents and which packs of skills and rules
files, whether to replace files that differ from the kit, and a last go-ahead after showing what it will do. A
flag answers a question in advance, so that question is not asked. Without a terminal (a pipe, CI) or with
--yes, nothing is asked: every agent is installed, the packs are the ones Enter would pick, and files that
differ are skipped unless --update.

Runs on Windows, macOS and Linux with Python 3.8 or later; needs nothing outside the standard library.
"""
import argparse
import re
import shutil
import sys
import textwrap
from pathlib import Path

KIT = Path(__file__).resolve().parent / "kit"
RULES = KIT / "templates" / "AGENTS.md"
PROJECT_TEMPLATE = KIT / "templates" / "project" / "AGENTS.md"
HOOK = KIT / "templates" / ".github" / "hooks" / "deny.json"
# The kit's language rules files: instructions/<name>.instructions.md, which Copilot loads for the files their applyTo
# matches.
INSTRUCTIONS = KIT / "instructions"
# The packs the scripts offer, in the order they are listed: (name, description, skills, rules files). Picking several
# installs the union. install-repo.py installs a pack's skills and rules files; install-user.py only its skills.
CODE_SKILLS = ["build-and-test", "write-tests", "dependency-upgrade", "api-contract-check"]
PACKS = [
    ("code", "Code, for every stack: build and test, write tests, upgrade dependencies, check API changes",
     CODE_SKILLS, []),
    ("java", "Java: the code pack, plus Spring Boot rules for .java files", CODE_SKILLS, ["springboot"]),
    ("node", "Node: the code pack, plus NestJS rules for .ts, .js and .json files", CODE_SKILLS, ["nestjs"]),
    ("scala", "Scala: the code pack and the sbt-and-play skill, plus Scala 2 and 3 rules for .scala and build.sbt files",
     CODE_SKILLS + ["sbt-and-play"], ["scala"]),
    ("python", "Python: the code pack (no Python rules yet)", CODE_SKILLS, []),
    ("flutter", "Flutter: the code pack, plus Dart and Flutter rules for .dart files", CODE_SKILLS, ["flutter"]),
    ("documents", "Documents: read Word, PDF, PowerPoint and Excel files, write Word and PowerPoint, work on PDFs and CSV files",
     ["read-documents", "csv-analysis", "pptx", "docx", "pdf"], []),
    ("planning", "Planning and writing: interview for a spec, draft from examples, capture a session, set up a repo's AGENTS.md",
     ["spec-interview", "draft-from-examples", "session-capture", "setup-project"], []),
]
# Skills a kit agent works through. They are installed with the agent even when no pack picked holds them.
AGENT_SKILLS = {
    "data-analyst": ["csv-analysis"],
    "document-reviewer": ["read-documents"],
}
# Kit files a skill copies into a project. They are installed inside the skill's own folder, so the skill finds
# them wherever it is installed and does not depend on where the kit was cloned.
SKILL_FILES = {
    "setup-project": [
        (PROJECT_TEMPLATE, "templates/project-AGENTS.md"),
        (KIT / "templates" / "research" / "AGENTS.md", "templates/research-AGENTS.md"),
    ],
}
# The job each kit agent gets in the delegation lines. install-user.py writes the lines for the agents installed for
# the user into the general rules; install-repo.py writes the lines for the agents installed in a repo into its AGENTS.md.
AGENT_JOBS = {
    "builder": "a fully specified change that a command can show worked",
    "reader": "facts about this repository's own code, logs or command output, with no advice",
    "kit-researcher": "a library, package, API or tool fact checked against what is installed",
    "verifier": "checking that a finished change works",
    "kit-reviewer": "reviewing a diff or pull request before it is merged",
    "data-analyst": "questions about CSV or other tabular data files",
    "document-reviewer": "reviewing a Word, PDF or PowerPoint document against a checklist or policy",
    "worker": "anything else where only the result is needed, such as an investigation across many files, "
              "a batch of small sub-tasks, a change in several steps or a draft",
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
    packs = ", ".join(p[0] for p in PACKS)
    parser.add_argument("--agents", metavar="NAMES", help=f"comma-separated agents to install, or all, or none. Kit agents: {agents}")
    parser.add_argument("--packs", metavar="NAMES", help=f"comma-separated packs to install, or all, or none. Kit packs: {packs}. "
                                                         "install-repo.py installs a pack's skills and rules files, install-user.py only its skills")
    parser.add_argument("--skills", metavar="NAMES", help="comma-separated single skills, or all, or none. Alone, it installs only these "
                                                          f"skills and asks no pack question; with --packs, these are added to the packs' skills. Kit skills: {skills}")
    parser.add_argument("--update", action="store_true", help="replace installed agent, skill, rules and hook files that differ from the kit, keeping each old one as <name>.bak")
    parser.add_argument("--rules", choices=("merge", "overwrite"),
                        help="when the rules file (copilot-instructions.md or AGENTS.md) already exists: merge updates only its "
                             "agents section (the default), overwrite replaces it with the kit's; either keeps the old one as .bak")
    parser.add_argument("--yes", "-y", action="store_true", help="ask nothing: use the flags given, all agents, and the packs Enter would pick")
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


def _parse_names(text, names, empty=None):
    """Turn 'all', 'none', '1,3' or 'worker,reader' into a list of names, or raise ValueError. An empty answer
    gives empty, or all names when empty is None."""
    text = text.strip().lower()
    if text == "":
        return list(names if empty is None else empty)
    if text == "all":
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


def pack_contents(pack_names):
    """Return (skills, rules files) for the packs named: the union of theirs, skills in kit order."""
    chosen = [p for p in PACKS if p[0] in pack_names]
    skills = [n for n, _ in kit_items("skill") if any(n in p[2] for p in chosen)]
    rules = []
    for p in chosen:
        rules += [r for r in p[3] if r not in rules]
    return skills, rules


def _ask_packs(default, notes):
    names = [p[0] for p in PACKS]
    width = min(shutil.get_terminal_size().columns, 120) - 1
    print("\nPacks in the kit:")
    for i, (name, desc, _, _) in enumerate(PACKS, 1):
        lines = textwrap.wrap(desc, width - 19, max_lines=2, placeholder=" ...") or [""]
        print(f"  {i:>2}. {name:<12} {lines[0]}")
        for more in lines[1:]:
            print(" " * 19 + more)
    for note in notes:
        print(textwrap.fill(note, width))
    shown = "all" if default == names else ", ".join(default) if default else "none"
    while True:
        answer = input(f"Which packs? Enter for {shown}; or numbers or names such as 1,3; or all; or none: ")
        try:
            return _parse_names(answer, names, default)
        except ValueError as bad:
            print(f"There is no pack {bad}. Use the numbers 1 to {len(names)} or the names listed.")


def choose_packs(args, interactive, parser, default, notes, with_rules):
    """Return (skills, rules files) to install. --skills alone gives only those skills and no rules files. Otherwise
    the packs come from --packs, the pack question (Enter gives default), or default when nothing is asked, and
    --skills adds to their skills. notes are printed under the list of packs. Without with_rules no rules file is
    returned."""
    skill_names = [n for n, _ in kit_items("skill")]
    pack_names = [p[0] for p in PACKS]
    single = []
    if args.skills is not None:
        try:
            single = _parse_names(args.skills, skill_names)
        except ValueError as bad:
            parser.error(f"unknown skill: {bad}; choose from {', '.join(skill_names)}")
        if args.packs is None:
            return single, []
    if args.packs is not None:
        try:
            packs = _parse_names(args.packs, pack_names)
        except ValueError as bad:
            parser.error(f"unknown pack: {bad}; choose from {', '.join(pack_names)}")
    elif interactive:
        packs = _ask_packs(default, notes)
    else:
        packs = list(default)
    packs = [n for n in pack_names if n in packs]
    skills, rules = pack_contents(packs)
    skills = [n for n in skill_names if n in skills or n in single]
    rules = rules if with_rules else []
    print(f"  Packs: {', '.join(packs) if packs else 'none'}")
    print(f"  Skills: {', '.join(skills) if skills else 'none'}")
    if with_rules:
        print(f"  Rules files: {', '.join(rules) if rules else 'none'}")
    return skills, rules


def add_agent_skills(agent_names, skill_names):
    """Return skill_names plus the skills the chosen agents work through (AGENT_SKILLS), saying which were added,
    because such an agent does not work without its skill whatever packs were picked."""
    added = [(s, a) for a in agent_names for s in AGENT_SKILLS.get(a, []) if s not in skill_names]
    for skill, agent in added:
        print(f"  Also skill {skill}, which the {agent} agent uses.")
    wanted = set(skill_names) | {s for s, _ in added}
    return [n for n, _ in kit_items("skill") if n in wanted]


def agents_after_install(agents_dir, agent_names):
    """The kit agents that agents_dir holds once this install is done: the ones chosen now and the ones already there."""
    return [n for n, _ in kit_items("agent") if n in agent_names or (agents_dir / f"{n}.agent.md").exists()]


def _find_section(text, heading):
    return re.search(rf"^{re.escape(heading)}[ \t]*\n.*?(?=^## |\Z)", text, re.M | re.S)


def with_agents_section(text, template, heading, agents, indent):
    """Return text with its section under heading replaced by the template's section of that name, in which the
    <placeholder> line becomes one job line per agent. The section is added at the end when text has none, and
    removed when there are no agents. The worker fallback line is added only when worker is one of the agents."""
    section = ""
    if agents:
        lines = [f"{indent}- {AGENT_JOBS.get(n, 'jobs that fit its description')} → `{n}`" for n in agents]
        if "worker" in agents:
            lines.append(f"{indent}- If the agent for a job is not installed, use `worker`.")
        own = _find_section(template, heading).group(0).splitlines()
        at = next(i for i, line in enumerate(own) if line.startswith("<") and line.endswith(">"))
        section = "\n".join(own[:at] + lines + own[at + 1:]).strip("\n") + "\n"
    match = _find_section(text, heading)
    if match:
        rest = text[match.end():]
        text = text[:match.start()] + (section + "\n" if section and rest else section) + rest
    elif section:
        text = text.rstrip("\n") + "\n\n" + section
    return text.rstrip("\n") + "\n"


def rules_file(path, template, heading, agents, indent, args, interactive):
    """Return (content, plan) for a rules file that carries an agents section. A missing file, or one that already
    matches, gets the kit's template with the section filled in and plan None. Otherwise the user chooses, by
    --rules or a question, to merge (keep the file and update only that section) or overwrite it with the kit's
    version; plan then says what happens, for install() to show and do without its replace question."""
    fresh = with_agents_section(template, template, heading, agents, indent)
    if not path.exists() or path.read_text(encoding="utf-8") == fresh:
        return fresh.encode("utf-8"), None
    choice = args.rules
    while choice is None and interactive:
        answer = input(f"\n{path.name} already exists and differs from the kit's. Merge (keep it and update only its "
                       f"\"{heading[3:]}\" section) or overwrite (replace it with the kit's)? Either keeps the old file "
                       f"as {path.name}.bak. [M/o] ").strip().lower()
        choice = {"": "merge", "m": "merge", "merge": "merge", "o": "overwrite", "overwrite": "overwrite"}.get(answer)
        if choice is None:
            print("Please answer m or o.")
    if choice == "overwrite":
        return fresh.encode("utf-8"), "overwrite with the kit's version"
    merged = with_agents_section(path.read_text(encoding="utf-8"), template, heading, agents, indent)
    return merged.encode("utf-8"), f"merge: update only its \"{heading[3:]}\" section"


def file_list(extra, base, agent_names, skill_names, rule_names=()):
    """Return [(content bytes, destination)] for the extra (source, destination) pairs and the chosen agents,
    skills and rules files. base is the folder that holds agents/, skills/ and instructions/."""
    agents, skills, instructions = base / "agents", base / "skills", base / "instructions"
    files = list(extra)
    files += [(KIT / "agents" / f"{n}.agent.md", agents / f"{n}.agent.md") for n in agent_names]
    files += [(INSTRUCTIONS / f"{n}.instructions.md", instructions / f"{n}.instructions.md") for n in rule_names]
    for n in skill_names:
        folder = KIT / "skills" / n
        files.append((folder / "SKILL.md", skills / n / "SKILL.md"))
        files += [(src, skills / n / rel) for src, rel in SKILL_FILES.get(n, [])]
        # Helper files that sit beside a skill's SKILL.md (scripts, examples) go with it.
        files += [(f, skills / n / f.relative_to(folder)) for f in sorted(folder.rglob("*"))
                  if f.is_file() and f.name not in ("SKILL.md", ".DS_Store") and "__pycache__" not in f.parts and f.suffix != ".pyc"]
    return [(c if isinstance(c, bytes) else c.read_bytes(), d) for c, d in files]


def install(files, dest, args, interactive, next_steps, plans=None):
    """Show what will happen, ask to go ahead when interactive, then write the files. plans maps a destination
    whose merge-or-overwrite question was already answered (see rules_file) to what happens to it; such a file is
    written without the replace question, keeping the old one as .bak."""
    def show(path):
        try:
            return str(path.relative_to(dest))
        except ValueError:
            return str(path)

    def replace_file(content, dst, verb):
        backup = dst.with_name(dst.name + ".bak")
        shutil.copyfile(dst, backup)
        dst.write_bytes(content)
        print(f"{verb + ':':<10} {show(dst)} (old file kept as {backup.name})")

    plans = plans or {}
    new = [(c, d) for c, d in files if not d.exists()]
    same = [(c, d) for c, d in files if d.exists() and d.read_bytes() == c]
    planned = [(c, d) for c, d in files if d.exists() and d.read_bytes() != c and d in plans]
    differ = [(c, d) for c, d in files if d.exists() and d.read_bytes() != c and d not in plans]

    print(f"\nInto {dest}:")
    print(f"  {len(new)} new file(s) to install")
    print(f"  {len(same)} file(s) already up to date")
    for _, d in planned:
        print(f"  {show(d)}: {plans[d]}")
    if differ:
        print(f"  {len(differ)} file(s) differ from the kit (changed by you, or from an older kit):")
        for _, d in differ:
            print(f"      {show(d)}")

    replace = args.update
    if differ and not replace and interactive:
        replace = ask_yes_no("Replace the files that differ? Each old file is kept beside it as <name>.bak.", False)
    if not new and not planned and not (differ and replace):
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
    for content, dst in planned:
        replace_file(content, dst, "merged" if plans[dst].startswith("merge") else "overwritten")
    for content, dst in differ:
        if replace:
            replace_file(content, dst, "replaced")
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
