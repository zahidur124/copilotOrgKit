---
name: session-capture
description: At the end of a session, summarize what was done and propose the lines a new session would need in the project's AGENTS.md or records; writes only the lines the user picks. Use when the user is wrapping up ("that's it for today", "wrap up", "what did we learn"), or asks what should go in AGENTS.md from this session.
---

# session-capture

1. **Summarize the session.** Say what was done in a few sentences, from this conversation and the commits it made.

2. **List what a new session would need.** Pick what this session had to work out that is not in the code, `git log` or the AGENTS.md files: a command that works, where something lives, a convention the code follows, a trap that cost time. Leave out what an existing line already says, what only mattered to this task, and a rule drawn from a single failure, because rules written from single failures piled up and misfired.

3. **Give each candidate its home.**
   - How a session works in this project: the project's AGENTS.md, in plain words, naming an item by what it is, where the project has one.
   - A fact about a file, service or vendor: the project's findings file, where the project has one.
   - Open work or a bug: a row in the project's task list, where the project has one.
   - Nothing goes in the user-level rules file (`~/.copilot/copilot-instructions.md`), because it is the base for every project.

4. **Propose, then stop.** Show each candidate as the exact line, the file it goes in, and one sentence on why a new session needs it. Write nothing until the user picks lines, because a file that loads into every session gets a new or changed rule only when the user asks for that rule.

5. **Write the lines the user picked, word for word.**
