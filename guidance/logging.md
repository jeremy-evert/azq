# Logging Guidance for azq

When you respond, format so `ask.py` and `uaskd` can produce a rich log.

## Format Rules
- Always treat the conversation as a transcript.
- Begin every assistant answer with clear prose, **outside** of command markers.
- When you want to suggest commands, wrap them like this:

::CMD
git status
::END_CMD

::CMD
git add .
git commit -m "Describe changes"
git push origin main
::END_CMD

- Do not prefix commands with $, !, or backticks.
- Explanations go outside command blocks.
- Commands go inside `::CMD`/`::END_CMD` only.

## Logging Goals
- `ask.py` will write:
  - USER question
  - ASSISTANT answer (with formatting preserved)
  - [snapshot: ...] pointer
- `uaskd` will append:
  - COMMAND: actual command string
  - RESULT: captured stdout/stderr (FAILED if exit non-zero)

This structure ensures `logs/chatlog.md` contains a complete transcript:
  1. Question
  2. Assistant prose
  3. Commands offered
  4. Commands executed with results

