# AZQ Codex Prompt Template: Stage 1

## Purpose

This document is a reusable prompt wrapper for sending **Stage 1 Finis storage tasks** to Codex one item at a time.

Its job is to keep Codex aligned with the AZQ doctrine while still producing small, practical patches.

The template is intentionally strict.
It exists to prevent scope drift, hidden architectural changes, and “helpful” overreach.

Use this template by pasting one JSON task from `AZQ_BUILD_TASKS_STAGE_1_WAVE_A.json` underneath the prompt body.

---

## Design Intent

Every Codex task submission should preserve these rules:

* stay inside the files named by the task
* keep the patch atomic
* do not silently broaden scope
* do not refactor unrelated modules
* preserve durable evidence
* summarize exactly what changed
* stop at the task boundary

The point is not to get the largest patch possible.
The point is to get a **clean, reviewable unit of work**.

---

## Reusable Prompt Template

Copy everything below and then append one task object from `AZQ_BUILD_TASKS_STAGE_1_WAVE_A.json`.

```text
You are helping implement Stage 1 of AZQ.

Read the repository files that are relevant to this task before making changes.
Use the attached architectural documents as constraints, especially:
- AZQ_IMPLEMENTATION_PLAN.md
- AZQ_BUILD_TASKS_STAGE_1.md
- AZQ_STATE_MODEL.md
- AZQ_FILESYSTEM_MODEL.md
- AZQ_COMMAND_MODEL.md

Your job is to complete exactly one task object.

Rules:

1. Stay inside the files named by the task unless a tiny supporting edit is absolutely required to make the code importable or runnable.
2. Keep the patch atomic and commit-sized.
3. Do not implement future tasks early.
4. Do not refactor unrelated modules.
5. Do not change architecture documents unless the task explicitly asks for it.
6. Preserve the current repository layout under `azq/`, not the aspirational `src/azq/` layout.
7. Prefer simple, readable code over clever abstractions.
8. Preserve backwards compatibility where practical during Stage 1.
9. If a task depends on behavior that does not yet exist, do the smallest correct implementation that satisfies the current task only.
10. Stop when the task’s acceptance criteria are satisfied.

Before editing files:
- briefly state what you think the task requires
- name the files you plan to inspect
- identify any dependency from `depends_on`

When coding:
- make only the smallest necessary changes
- keep file formats human-readable and diff-friendly
- preserve durable evidence on disk where relevant
- avoid destructive behavior

After coding:
- show a concise summary of what changed
- list the files changed
- state how the acceptance criteria were satisfied
- mention any tests or checks you ran
- state any follow-up risk or note, but do not continue into the next task

If the task is underspecified, make the smallest reasonable choice and explain it briefly.
If the task cannot be completed cleanly without violating the rules, stop and explain the blocker rather than broadening scope.

Task object:
[paste one JSON task here]
```

---

## Minimal Operator Workflow

For each task:

1. copy the reusable prompt template
2. paste one JSON task object under `Task object:`
3. send it to Codex
4. review the patch
5. run the repo locally if needed
6. commit if clean
7. move to the next task

This preserves a steady build rhythm:

```text
one task
-> one patch
-> one review
-> one commit
```

---

## Recommended Add-On Line

If you want Codex to be even more conservative, add this line before the task object:

```text
Do not “help” by beginning the next task.
```

That one sentence is often worth its weight in steel.

---

## Suggested Short Version

When you want a more compact operator prompt, use this version:

```text
Read the relevant repository files and complete exactly one Stage 1 AZQ task.
Stay inside the files named by the task.
Keep the patch atomic.
Do not implement future tasks early.
Do not refactor unrelated modules.
Use the current `azq/` repo layout.
After editing, summarize changes, list files changed, and explain how the acceptance criteria were satisfied.
Stop at the task boundary.

Task object:
[paste one JSON task here]
```

---

## Why This Template Exists

Codex is often strongest when the task is clear and bounded.
It is often weakest when it is allowed to wander.

This template gives it:

* the architectural constraints
* the current repo reality
* the atomic task boundary
* the expected output format

That keeps the work aligned with AZQ’s craft discipline.

---

## Closing

The goal of this template is not to make Codex timid.
It is to make Codex precise.

A good patch should feel like a clean stone set into a wall.
Not a wheelbarrow of extra bricks dumped into the garden.

