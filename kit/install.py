#!/usr/bin/env python3
"""Copy this kit's agents, skills, working rules and deny hook to where Copilot reads them.

  python install.py user [--update]        into your Copilot config ($COPILOT_HOME or ~/.copilot); applies to every repo you open
  python install.py repo [dir] [--update]  into one repo (default: the current directory); you decide whether to commit them

A file that is missing is installed. A file identical to the kit's copy is left alone.
A file that differs is skipped, unless --update is given: then the old file is kept as <name>.bak and replaced.
Runs on Windows, macOS and Linux with Python 3.8 or later; needs nothing outside the standard library.
"""
import argparse
import filecmp
import os
import shutil
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent


def targets(mode, repo_dir):
    """Return (destination root, list of (source, destination) pairs)."""
    if mode == "user":
        dest = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot")
        rules, hooks, agents, skills = dest / "copilot-instructions.md", dest / "hooks", dest / "agents", dest / "skills"
    else:
        dest = Path(repo_dir).resolve()
        if not (dest / ".git").exists():
            print(f"warning: {dest} is not a git repository root; Copilot reads .github/hooks/ only at the root", file=sys.stderr)
        rules, hooks, agents, skills = dest / "AGENTS.md", dest / ".github" / "hooks", dest / ".github" / "agents", dest / ".github" / "skills"
    pairs = [
        (KIT / "templates" / "AGENTS.md", rules),
        (KIT / "templates" / ".github" / "hooks" / "deny.json", hooks / "deny.json"),
    ]
    pairs += [(f, agents / f.name) for f in sorted((KIT / "agents").glob("*.agent.md"))]
    pairs += [(f, skills / f.parent.name / "SKILL.md") for f in sorted((KIT / "skills").glob("*/SKILL.md"))]
    return dest, pairs


def main():
    parser = argparse.ArgumentParser(description="Install the Copilot kit.")
    parser.add_argument("mode", choices=["user", "repo"])
    parser.add_argument("dir", nargs="?", default=".", help="repo mode only: the repository root (default: current directory)")
    parser.add_argument("--update", action="store_true", help="replace installed files that differ from the kit, keeping each old one as <name>.bak")
    args = parser.parse_args()
    if args.mode == "user" and args.dir != ".":
        parser.error("a directory is only taken in repo mode")

    _, pairs = targets(args.mode, args.dir)
    differ = 0
    for src, dst in pairs:
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"installed: {dst}")
        elif filecmp.cmp(src, dst, shallow=False):
            print(f"unchanged: {dst}")
        elif args.update:
            backup = dst.with_name(dst.name + ".bak")
            shutil.copyfile(dst, backup)
            shutil.copyfile(src, dst)
            print(f"replaced:  {dst} (old file kept as {backup.name})")
        else:
            differ += 1
            print(f"skipped, differs from the kit: {dst}")
    if differ:
        print(f"\n{differ} file(s) differ from the kit; run again with --update to replace them (the old ones are kept as .bak).")


if __name__ == "__main__":
    main()
