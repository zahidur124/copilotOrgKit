# Claude Design prompt: Copilot kit training deck

## How to use

1. In Claude Design, start a new slide deck project.
2. Attach `outline.md` and `kit-content.md` from this folder. If your company has a design system or a slide template in Claude Design, select it too.
3. Paste the prompt below.
4. Check every slide against `kit-content.md` before presenting. It is the source of truth.

## Prompt

Build a training slide deck titled "Getting started with the Copilot kit: agents, skills and working rules".

Audience: software developers at our company who already use GitHub Copilot for chat and completions, but have not used custom agents, agent skills, instruction files or hooks. The session lasts about 45 minutes and includes one live demo.

Goal: by the end, each developer knows what is in the kit, can install it in user or repo mode, knows which agent or skill to reach for, and understands what the safety hook does and does not protect against.

Sources:
- `outline.md` gives the slide order, the on-slide points, the speaker notes and a visual idea for each slide. Follow its order and slide count. You may tighten wording and choose better visuals.
- `kit-content.md` is the source of truth for facts: file paths, commands, agent and skill names, what the hook blocks, and the limits. Do not add features, numbers or claims that are not in it. If a slide needs a fact that is missing, leave a visible placeholder like `[TODO: …]`, don't guess.

Content rules:
- Plain, direct language. Short sentences. Explain a term the first time it appears ("a custom agent is…").
- At most four short points per slide. Detail goes in the speaker notes.
- Show commands, file paths and file names in a monospace style, exactly as written in the sources (for example `./install.sh user`, `~/.copilot/agents/`, `AGENTS.md`).
- Be honest on the guardrails slide: state the hook's limits as plainly as its protections.
- No marketing tone, no stock-photo filler, no emoji.

Design:
- Clean, technical look for an engineering audience. Use our design system if one is attached. If not, use a neutral palette with one accent colour and generous white space.
- Prefer diagrams and tables to bullet lists where the outline suggests them. Planned visuals:
  - one overview diagram of the kit (agents, skills, rules, hook, installer);
  - a user-mode vs repo-mode comparison showing where files land;
  - an "which agent do I use?" decision table;
  - a slide that introduces the live demo and lists what to watch for.
- Use clearly labelled placeholder frames where a screenshot belongs (for example "Screenshot: Copilot agent picker").
- Code snippets should be short (under about 8 lines) and readable from the back of a room.

Output: 16:9 slides with speaker notes on every slide. Close with a one-slide getting-started checklist and a Q&A slide.
