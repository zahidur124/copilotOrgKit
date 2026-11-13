#!/usr/bin/env python3
"""Copy this kit's agents, skills, working rules and deny hook to where Copilot reads them.

  python install.py user [--update]        into your Copilot config ($COPILOT_HOME or ~/.copilot); applies to every repo you open
  python install.py repo [dir] [--update]  into one repo (default: the current directory); you decide whether to commit them
  add --agents worker,reader                to install only the agents named (default: all of them)
  add --skills spec-interview               to install only the skills named (default: all of them)

In a repo the working rules go in .github/instructions/kit.instructions.md, not AGENTS.md, so the repo's own AGENTS.md is never touched.

A file that is missing is installed. A file identical to the kit's copy is left alone.
A file that differs is skipped, unless --update is given: then the old file is kept as <name>.bak and replaced.
Runs on Windows, macOS and Linux with Python 3.8 or later; needs nothing outside the standard library.
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
RULES = KIT / "templates" / "AGENTS.md"
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


def targets(mode, repo_dir, agent_names, skill_names):
    """Return a list of (content, destination) pairs."""
    if mode == "user":
        dest = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot")
        rules, header = dest / "copilot-instructions.md", b""
        hooks, agents, skills = dest / "hooks", dest / "agents", dest / "skills"
    else:
        dest = Path(repo_dir).resolve()
        if not (dest / ".git").exists():
            print(f"warning: {dest} is not a git repository root; Copilot reads .github/hooks/ only at the root", file=sys.stderr)
        rules, header = dest / ".github" / "instructions" / "kit.instructions.md", REPO_RULES_HEADER
        hooks, agents, skills = dest / ".github" / "hooks", dest / ".github" / "agents", dest / ".github" / "skills"
        old = dest / "AGENTS.md"
        if old.exists() and old.read_bytes().startswith(RULES.read_bytes().splitlines(keepends=True)[0]):
            print(f"warning: {old} looks like the kit's rules from an earlier install; they now live in {rules.relative_to(dest)}. "
                  "Delete AGENTS.md unless you added your own rules to it, or Copilot reads the rules twice.", file=sys.stderr)
    files = [(header + RULES.read_bytes(), rules), (KIT / "templates" / ".github" / "hooks" / "deny.json", hooks / "deny.json")]
    files += [(KIT / "agents" / f"{n}.agent.md", agents / f"{n}.agent.md") for n in agent_names]
    files += [(KIT / "skills" / n / "SKILL.md", skills / n / "SKILL.md") for n in skill_names]
    files += [(src, skills / n / rel) for n in skill_names for src, rel in SKILL_FILES.get(n, [])]
    # Helper files that sit beside a skill's SKILL.md (scripts, examples) go with it.
    for n in skill_names:
        folder = KIT / "skills" / n
        files += [(f, skills / n / f.relative_to(folder)) for f in sorted(folder.rglob("*"))
                  if f.is_file() and f.name not in ("SKILL.md", ".DS_Store") and "__pycache__" not in f.parts and f.suffix != ".pyc"]
    return [(c if isinstance(c, bytes) else c.read_bytes(), d) for c, d in files]


def main():
    parser = argparse.ArgumentParser(description="Install the Copilot kit.")
    parser.add_argument("mode", choices=["user", "repo"])
    parser.add_argument("dir", nargs="?", default=".", help="repo mode only: the repository root (default: current directory)")
    parser.add_argument("--update", action="store_true", help="replace installed files that differ from the kit, keeping each old one as <name>.bak")
    all_agents = sorted(f.name[: -len(".agent.md")] for f in (KIT / "agents").glob("*.agent.md"))
    all_skills = sorted(f.parent.name for f in (KIT / "skills").glob("*/SKILL.md"))
    parser.add_argument("--agents", metavar="NAME,NAME", help="install only these agents, comma-separated (default: all): " + ", ".join(all_agents))
    parser.add_argument("--skills", metavar="NAME,NAME", help="install only these skills, comma-separated (default: all): " + ", ".join(all_skills))
    args = parser.parse_args()
    if args.mode == "user" and args.dir != ".":
        parser.error("a directory is only taken in repo mode")

    def chosen(value, available, kind):
        if value is None:
            return available
        names = [n.strip() for n in value.split(",") if n.strip()]
        unknown = [n for n in names if n not in available]
        if unknown or not names:
            parser.error(f"unknown {kind}: {', '.join(unknown) or '(none given)'}; choose from {', '.join(available)}")
        return names

    agent_names = chosen(args.agents, all_agents, "agent")
    skill_names = chosen(args.skills, all_skills, "skill")
    if "worker" not in agent_names:
        print("note: the working rules hand work to the worker agent, which you are not installing", file=sys.stderr)

    differ = 0
    for content, dst in targets(args.mode, args.dir, agent_names, skill_names):
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(content)
            print(f"installed: {dst}")
        elif dst.read_bytes() == content:
            print(f"unchanged: {dst}")
        elif args.update:
            backup = dst.with_name(dst.name + ".bak")
            shutil.copyfile(dst, backup)
            dst.write_bytes(content)
            print(f"replaced:  {dst} (old file kept as {backup.name})")
        else:
            differ += 1
            print(f"skipped, differs from the kit: {dst}")
    if differ:
        print(f"\n{differ} file(s) differ from the kit; run again with --update to replace them (the old ones are kept as .bak).")


if __name__ == "__main__":
    main()
