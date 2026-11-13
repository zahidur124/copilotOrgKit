#!/usr/bin/env python3
"""Install the kit into your own Copilot config, so it applies in every repo you open. Nothing is committed anywhere.

The config folder is $COPILOT_HOME, or ~/.copilot when that is not set. The rules go in copilot-instructions.md,
the hook in hooks/deny.json, and the agents and skills in agents/ and skills/.
"""
import os
from pathlib import Path

import installer as kit

EXAMPLES = """examples:
  python install-user.py                          asks which agents and skills, then installs
  python install-user.py --yes                    installs everything without asking
  python install-user.py --agents worker,reader --skills none --yes
  python install-user.py --update --yes           brings an earlier install up to date"""


def main():
    parser = kit.make_parser("Install the Copilot kit into your Copilot config ($COPILOT_HOME or ~/.copilot).", EXAMPLES)
    args = parser.parse_args()
    interactive = kit.is_interactive(args)
    dest = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot")
    if interactive:
        print(f"Copilot kit: install for you, in every repo you open.\nYour Copilot config folder is {dest}")
    agent_names, skill_names = kit.choose_agents_and_skills(args, interactive, parser)
    files = kit.file_list(dest / "copilot-instructions.md", b"", dest, agent_names, skill_names)
    kit.install(files, dest, args, interactive,
                "Start a new Copilot session to load them. In Copilot CLI, `copilot instruction list` shows the rules file it loads.")


if __name__ == "__main__":
    kit.run(main)
