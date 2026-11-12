---
name: spec-interview
description: Turn a rough feature idea into a written spec by getting real examples of the result from the user, working out the steps that produce them, and asking the user only what the steps cannot settle, then writing the spec file. Use when the user wants a spec, requirements or a PRD written for a feature, says "interview me" about an idea, or describes a feature too loosely to build from.
---

# spec-interview

Feature: the idea the user gave.

1. **Read before asking.** Read the project's AGENTS.md, its existing spec and design files, and the code the feature touches. Answer what the repo can answer yourself, so every question you ask is one only the user can settle.

2. **Get examples first.** Before any other question, get real cases from the user: a time the feature
   would have helped, what came in, and what the user would have wanted to see or be told. Offer cases
   you found in the repo, its data or real history for the user to confirm or correct. Write each one in
   the user's words. An example comes first because it shows a right answer and the input it comes from,
   and a description of the feature does not.

3. **Work out the steps yourself.** Write the steps that take the first example's input to its answer, in
   plain words: what each step takes in and what it works out. This is your work and not a question for
   the user, who has said what they want and not how. Work the steps out backwards: start from the
   example's answer, ask what had to be known just before it could be given, and repeat until you reach
   the input, because a step found this way is one the answer needs. Where you do not know how a step is
   done, find out how it is done today. Show the user the steps with the example walked through them, and correct them
   from what the user says.

4. **Ask only where a step needs the user.** A question goes to the user when a step cannot be written
   without a choice that is theirs: what counts as a right answer, what they would act on, what they will
   not accept. Ask the user directly: up to four questions at a time, each option says what it implies, your
   recommended option first, and each question names the step it belongs to. What the user sees, the
   empty and error states, limits, and how the result is delivered or measured are asked when the steps
   reach them, and whatever has a usual default gets that default, stated. Stop when the first example
   walks through every step with no gap that is the user's to fill.

5. **Write the spec where the project keeps specs.** Follow the project's AGENTS.md and the file's own
   header. In a project that keeps a spec and a design file (by default `docs/spec.md` and `docs/design.md`),
   the examples, the steps and the product answers go in the spec in the user's words, and implementation
   answers go in the design file. With no spec file, write `docs/spec.md`. Use the user's answers as given,
   and mark anything still open as an open question with the step it blocks.

6. **Report.** Give the file path, the steps with the first example walked through them, and the open
   questions, if any.
