#!/usr/bin/env python3
"""Copy this kit's agents, skills, working rules and deny hook to where Copilot reads them.

  python install.py user [--update]        into your Copilot config ($COPILOT_HOME or ~/.copilot); applies to every repo you open
  python install.py repo [dir] [--update]  into one repo (default: the current directory); you decide whether to commit them

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


def targets(mode, repo_dir):
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
    files += [(f, agents / f.name) for f in sorted((KIT / "agents").glob("*.agent.md"))]
    files += [(f, skills / f.parent.name / "SKILL.md") for f in sorted((KIT / "skills").glob("*/SKILL.md"))]
    return [(c if isinstance(c, bytes) else c.read_bytes(), d) for c, d in files]


def main():
    parser = argparse.ArgumentParser(description="Install the Copilot kit.")
    parser.add_argument("mode", choices=["user", "repo"])
    parser.add_argument("dir", nargs="?", default=".", help="repo mode only: the repository root (default: current directory)")
    parser.add_argument("--update", action="store_true", help="replace installed files that differ from the kit, keeping each old one as <name>.bak")
    args = parser.parse_args()
    if args.mode == "user" and args.dir != ".":
        parser.error("a directory is only taken in repo mode")

    differ = 0
    for content, dst in targets(args.mode, args.dir):
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
