# AZQ Codex Runbook: Stage 1, Wave A

## Purpose

This runbook defines how to execute **Stage 1, Wave A** using Codex in a disciplined loop.

Wave A is the **storage foundation** of Stage 1.
It covers the first six tasks in `planning/stage_1/wave_a/tasks.json`:

* create Finis storage scaffolding
* add canonical path constants and directory helpers
* define the normalized goal schema
* implement markdown goal serialization and parsing
* implement file-backed goal reads and ID allocation
* add the read-only legacy `goals.json` reader

The runbook exists to make Codex useful without letting it wander.

Its goal is not maximum automation.
Its goal is **bounded, reviewable progress**.

---

## Wave A Intent

Wave A should leave the repository with a real storage foundation for Finis, but without prematurely refactoring all Finis commands.

By the end of Wave A:

* `azq/finis/storage.py` should exist
* canonical Finis path decisions should live there
* the normalized goal schema should be defined there
* markdown goal record parsing and serialization should exist
* file-backed goal reads should exist
* legacy JSON should be readable as migration input only

Wave A should **not** yet:

* migrate all live command handlers
* remove legacy JSON behavior from every command
* implement Formam, Agenda, or Domum
* broaden into Stage 1 Wave B or C

---

## Operator Inputs

Before starting, make sure these files exist and are readable:

* `planning/stage_1/wave_a/tasks.json`
* `codex/templates/AZQ_CODEX_PROMPT_TEMPLATE_STAGE_1.md`
* `planning/stage_1/overview.md`
* `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md`
* `docs/architecture/AZQ_STATE_MODEL.md`
* `docs/architecture/AZQ_FILESYSTEM_MODEL.md`
* `docs/architecture/AZQ_COMMAND_MODEL.md`

The primary task source for this runbook is the JSON list.

Each Codex submission should use **one task object only**.

The preferred staged runner entrypoint is `codex/tools/azq_codex_task_runner.py`.
The root-level `azq_codex_task_runner.py` and `azq_codex_stage1_task_runner.py` files remain only as thin compatibility paths for existing operator habits.

---

## Wave A Task Order

Run tasks in this order:

1. `STAGE1-WAVEA-01`
2. `STAGE1-WAVEA-02`
3. `STAGE1-WAVEA-03`
4. `STAGE1-WAVEA-04`
5. `STAGE1-WAVEA-05`
6. `STAGE1-WAVEA-06`

Do not reorder unless a manual review determines that one task is blocked by missing prior work.

The dependency chain is intentional.

---

## Normal Flow

For each task, use the following sequence.

### Step 1: Select one task

Pick exactly one JSON task object from `planning/stage_1/wave_a/tasks.json`.

### Step 2: Build the prompt

Use `codex/templates/AZQ_CODEX_PROMPT_TEMPLATE_STAGE_1.md`.

Paste in:

* the reusable prompt template
* one task object under `Task object:`

Optional but recommended line:

```text
Do not “help” by beginning the next task.
```

### Step 3: Submit to Codex

Send the prompt to Codex and let it prepare a patch.

### Step 4: Review Codex response before accepting anything

Look for:

* did it stay inside the allowed files?
* did it keep the patch atomic?
* did it avoid future-task creep?
* did it preserve the real `azq/` repo layout?

If the answer is clearly no, reject the patch and resubmit with corrective feedback before running checks.

### Step 5: Run checks

Run the checks appropriate for the task.

### Step 6: Evaluate checks

If checks pass:

* inspect the diff
* commit if clean
* update progress tracking

If checks fail:

* enter the **failed-check repair flow** below

### Step 7: Commit

Commit only after:

* the acceptance criteria are satisfied
* the checks pass or are intentionally waived with reason
* the patch still feels atomic

---

## Failed-Check Repair Flow

This is the heart of the runbook.

If a task fails checks, do **not** ask Codex vaguely to “try again.”

Instead, resubmit with:

1. the **original prompt template**
2. the **same JSON task object**
3. the **failing check output**
4. a short repair instruction

### Repair instruction template

```text
Your previous patch did not satisfy the checks below.
Revise only what is necessary to satisfy the task and the failing checks.
Do not broaden scope.
Do not begin the next task.

Failing checks:
[paste exact output here]
```

### Why this matters

This keeps the retry loop tethered to:

* original task intent
* exact architectural constraints
* concrete failure evidence

That turns retries into **guided repair** instead of blind flailing.

---

## Retry Cap

Every task gets a bounded number of attempts.

Recommended limit:

* **Attempt 1**: original task submission
* **Attempt 2**: repair attempt 1
* **Attempt 3**: repair attempt 2

If the patch still fails after Attempt 3:

* stop automated retries
* inspect manually
* decide whether to:

  * make a small human correction
  * rewrite the task more clearly
  * split the task into smaller pieces

Do not let Codex loop forever.

A bounded loop protects the architecture.

---

## Check Types

Use two classes of checks.

### Hard checks

These should usually pass before commit.

Examples:

* file imports cleanly
* expected file exists
* parser/serializer round-trip works
* deterministic listing works
* exact lookup works
* legacy reader behaves correctly on missing input

### Human checks

These require judgment.

Examples:

* patch stayed inside allowed files
* patch remains atomic
* code is readable
* output format is human-friendly
* no architectural drift occurred
* no future task was partially implemented

Hard checks catch breakage.
Human checks preserve discipline.

---

## Suggested Checks For Wave A

These checks should be chosen according to the task.

### Common baseline checks

```bash
python -m compileall azq
```

If there are tests already in place for the task, run those too.

### Task-specific examples

#### For `STAGE1-WAVEA-01`

* verify `azq/finis/storage.py` imports cleanly

#### For `STAGE1-WAVEA-02`

* verify path helpers return expected paths
* verify directory creation helper works in a temp location or safely in repo context

#### For `STAGE1-WAVEA-03`

* verify normalization fills required fields
* verify legacy `goal` becomes canonical `title`

#### For `STAGE1-WAVEA-04`

* verify one normalized goal record can round-trip through markdown serialization and parsing

#### For `STAGE1-WAVEA-05`

* verify goal file listing is deterministic
* verify exact `goal_id` lookup works
* verify next id generation is stable

#### For `STAGE1-WAVEA-06`

* verify missing `goals.json` is handled cleanly
* verify malformed JSON fails diagnostically
* verify no code writes to legacy JSON

---

## Commit Gate

Do **not** commit a task patch unless all of these are true:

1. the task’s acceptance criteria are satisfied
2. hard checks pass, or an explicit waiver is written down
3. the patch still feels atomic
4. the patch stayed inside the intended scope
5. the diff is understandable enough to review later

If any of these are false, do not commit yet.

---

## Progress Tracking

Track each task using a simple status table.

Suggested statuses:

* `todo`
* `in_progress`
* `codex_submitted`
* `repair_loop`
* `passed_checks`
* `committed`
* `blocked`

Example:

| Task ID         | Status      | Notes                            |
| --------------- | ----------- | -------------------------------- |
| STAGE1-WAVEA-01 | committed   | storage.py scaffold added        |
| STAGE1-WAVEA-02 | repair_loop | helper path bug on first attempt |
| STAGE1-WAVEA-03 | todo        |                                  |

You can keep this in a scratch markdown file, a notebook, or a JSON status file if you want to automate it later.

The important thing is that the operator can always answer:

* what task are we on?
* what failed?
* what passed?
* what was committed?

---

## Recommended Operator Rhythm

Use this loop:

```text
pick one task
-> build prompt
-> submit to Codex
-> review patch
-> run checks
-> repair if needed
-> commit
-> update progress
-> move to next task
```

This rhythm is boring on purpose.

Boring is good.
Boring is how foundations stay level.

---

## Stop Conditions

Stop the session if any of these happen:

* repeated failed repairs exceed the retry cap
* Codex keeps escaping the task boundary
* checks reveal a contradiction in the doctrine docs
* a patch would require starting Wave B work early
* operator confidence drops below “I understand this diff”

Stopping is allowed.
Stopping is cheaper than smuggling confusion into the foundation.

---

## Suggested Commit Message Pattern

Use concise commit messages tied to the task.

Examples:

* `add finis storage module scaffolding`
* `add finis storage path constants and helpers`
* `add canonical finis goal normalization`
* `add markdown goal file read write format`
* `add file backed finis goal reads and id allocation`
* `add read only legacy finis json reader`

This keeps history aligned with the task list.

---

## Definition Of Success For Wave A

Wave A succeeds when:

* all six Wave A tasks are committed cleanly
* `azq/finis/storage.py` becomes the emerging storage authority
* no command handlers have been broadly refactored yet
* the repo has a credible storage foundation for Stage 1 Wave B

Wave A is not the end of Stage 1.
It is the stone footing under Stage 1.

---

## Closing

This runbook is designed to keep Codex useful, bounded, and honest.

A good Wave A session should feel like careful masonry:

one stone,
one fit,
one check,
one set.

Then the next stone.
