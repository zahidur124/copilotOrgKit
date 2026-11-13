#!/usr/bin/env python3
"""Install the kit into your own Copilot config, so it applies in every repo you open. Nothing is committed anywhere.

The config folder is $COPILOT_HOME, or ~/.copilot when that is not set. The kit's general working rules go in
copilot-instructions.md, with delegation lines for the agents installed there, and the agents and the chosen packs'
skills in agents/ and skills/. The safety hook and the packs' language rules files are not installed here:
install-repo.py puts them in each repository.
"""
import os
import sys
from pathlib import Path

import installer as kit

EXAMPLES = """examples:
  python install-user.py                          asks which agents and packs, then installs
  python install-user.py --yes                    installs all agents and all packs' skills without asking
  python install-user.py --packs code,documents --yes
  python install-user.py --agents worker,reader --packs none --yes
  python install-user.py --skills csv-analysis --yes  only that skill (no packs), and all agents
  python install-user.py --update --yes           brings an earlier install up to date"""


def main():
    parser = kit.make_parser("Install the Copilot kit into your Copilot config ($COPILOT_HOME or ~/.copilot).", EXAMPLES)
    args = parser.parse_args()
    interactive = kit.is_interactive(args)
    dest = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot")
    if interactive:
        print(f"Copilot kit: install for you, in every repo you open.\nYour Copilot config folder is {dest}")
    old_hook = dest / "hooks" / "deny.json"
    if old_hook.exists() and old_hook.read_bytes() == kit.HOOK.read_bytes():
        print(f"note: {old_hook} is the kit's safety hook from an earlier install. The hook is now set up per repository "
              "by install-repo.py; delete this copy if you want it only there.", file=sys.stderr)
    agent_names = kit.choose("agent", args.agents, interactive, parser)
    skill_names, _ = kit.choose_packs(args, interactive, parser, [p[0] for p in kit.PACKS],
                                      ["This installs only the packs' skills. Language rules files belong to a repo, so "
                                       "install-repo.py installs them there."], with_rules=False)
    rules_path = dest / "copilot-instructions.md"
    rules, plan = kit.rules_file(rules_path, kit.RULES.read_text(encoding="utf-8"), "## Handing work to agents",
                                 kit.agents_after_install(dest / "agents", agent_names), "  ", args, interactive)
    files = kit.file_list([(rules, rules_path)], dest, agent_names, skill_names)
    kit.install(files, dest, args, interactive,
                "Start a new Copilot session to load them. In Copilot CLI, `copilot instruction list` shows the rules file it loads.",
                {rules_path: plan} if plan else None)


if __name__ == "__main__":
    kit.run(main)
