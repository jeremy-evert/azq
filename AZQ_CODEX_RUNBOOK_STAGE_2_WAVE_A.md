# AZQ Codex Runbook: Stage 2, Wave A

## Purpose

This runbook defines how to execute **Stage 2, Wave A** using Codex in a disciplined loop.

Wave A is the **storage and record foundation** of Stage 2.
It covers the first nine tasks in `AZQ_BUILD_TASKS_STAGE_2_WAVE_A.json`:

* create Formam package and storage scaffolding
* add canonical Formam path constants and directory helpers
* define the normalized deliverable schema
* implement markdown deliverable serialization and parsing
* implement file-backed deliverable reads and id allocation
* add canonical goal-parent validation helpers
* define the normalized goal-map schema
* implement goal-map file read/write format
* add canonical Formam write helpers for deliverables and maps

The runbook exists to make Codex useful without letting it wander.

Its goal is not maximum automation.
Its goal is **bounded, reviewable progress**.

---

## Wave A Intent

Wave A should leave the repository with a real storage foundation for Formam, but without prematurely expanding into rich planning behavior.

By the end of Wave A:

* `azq/formam/storage.py` should exist
* canonical Formam path decisions should live there
* the normalized deliverable schema should be defined there
* markdown deliverable parsing and serialization should exist
* file-backed deliverable reads should exist
* goal-parent validation should exist
* the normalized goal-map schema should exist
* markdown goal-map parsing and serialization should exist
* write helpers for deliverables and maps should exist

Wave A should **not** yet:

* introduce full Formam CLI commands
* generate complex deliverable sets automatically
* broaden into Agenda or task decomposition
* collapse deliverables into task lists
* broaden into Stage 2 Wave B or C

---

## Operator Inputs

Before starting, make sure these files exist and are readable:

* `AZQ_BUILD_TASKS_STAGE_2_WAVE_A.json`
* `AZQ_CHECKS_STAGE_2_WAVE_A.json`
* `AZQ_BUILD_TASKS_STAGE_2.md`
* `AZQ_IMPLEMENTATION_PLAN.md`
* `AZQ_STATE_MODEL.md`
* `AZQ_FILESYSTEM_MODEL.md`
* `AZQ_COMMAND_MODEL.md`

Recommended additional context:

* `README.md`
* `AZQ_ENGINE_SPEC.md`
* `AZQ_STAGE_1_WAVE_C_CLOSEOUT.md`

The primary task source for this runbook is the JSON list.

Each Codex submission should use **one task object only**.

The preferred staged runner entrypoint is `azq_codex_task_runner.py`.
The older `azq_codex_stage1_task_runner.py` name remains only as a compatibility path for existing operator habits.

---

## Wave A Task Order

Run tasks in this order:

1. `STAGE2-WAVEA-01`
2. `STAGE2-WAVEA-02`
3. `STAGE2-WAVEA-03`
4. `STAGE2-WAVEA-04`
5. `STAGE2-WAVEA-05`
6. `STAGE2-WAVEA-06`
7. `STAGE2-WAVEA-07`
8. `STAGE2-WAVEA-08`
9. `STAGE2-WAVEA-09`

Do not reorder unless a manual review determines that one task is blocked by missing prior work.

The dependency chain is intentional.

---

## Normal Flow

For each task, use the following sequence.

### Step 1: Select one task

Pick exactly one JSON task object from `AZQ_BUILD_TASKS_STAGE_2_WAVE_A.json`.

### Step 2: Build the prompt

Use the Stage 1 prompt template unless and until a Stage 2-specific prompt wrapper exists.

Use:

* `AZQ_CODEX_PROMPT_TEMPLATE_STAGE_1.md`

Paste in:

* the reusable prompt template
* one task object under `Task object:`

Optional but recommended line:

```text
Do not "help" by beginning the next task.
````

Optional but often useful Stage 2 constraint line:

```text
Do not introduce task-list behavior. Formam defines deliverables and maps, not execution tasks.
```

### Step 3: Submit to Codex

Send the prompt to Codex and let it prepare a patch.

### Step 4: Review Codex response before accepting anything

Look for:

* did it stay inside the allowed files?
* did it keep the patch atomic?
* did it avoid future-task creep?
* did it preserve the real `azq/` repo layout?
* did it keep Formam focused on deliverables and maps instead of tasks?

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
* parent-goal validation works
* deliverable and map write helpers create canonical files

### Human checks

These require judgment.

Examples:

* patch stayed inside allowed files
* patch remains atomic
* code is readable
* markdown formats are human-friendly
* no architectural drift occurred
* no task-planning behavior was introduced early
* no future wave behavior was partially implemented

Hard checks catch breakage.
Human checks preserve discipline.

---

## Suggested Checks For Wave A

These checks should be chosen according to the task.

### Common baseline checks

```bash
python -m compileall azq
python -m unittest discover -s tests -v
```

If no unit tests exist yet for the task, rely on the checks recipe and direct module-level checks.

### Task-specific examples

#### For `STAGE2-WAVEA-01`

* verify `azq/formam/__init__.py` exists
* verify `azq/formam/storage.py` imports cleanly

#### For `STAGE2-WAVEA-02`

* verify path helpers return canonical deliverables/maps paths
* verify directory creation helper works in a temp location or safely in repo context

#### For `STAGE2-WAVEA-03`

* verify normalization fills required deliverable fields
* verify dependency fields normalize into lists

#### For `STAGE2-WAVEA-04`

* verify one normalized deliverable record can round-trip through markdown serialization and parsing

#### For `STAGE2-WAVEA-05`

* verify deliverable file listing is deterministic
* verify exact `deliverable_id` lookup works
* verify next deliverable id generation is stable

#### For `STAGE2-WAVEA-06`

* verify parent-goal validation uses exact goal lookup through Finis storage
* verify missing parent goal fails cleanly and inspectably

#### For `STAGE2-WAVEA-07`

* verify normalization fills required goal-map fields
* verify deliverable relationship fields normalize correctly

#### For `STAGE2-WAVEA-08`

* verify one normalized goal-map record can round-trip through markdown serialization and parsing

#### For `STAGE2-WAVEA-09`

* verify one deliverable file and one goal-map file can be written canonically
* verify write helpers each rewrite exactly one file

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

| Task ID         | Status      | Notes                                    |
| --------------- | ----------- | ---------------------------------------- |
| STAGE2-WAVEA-01 | committed   | formam package scaffold added            |
| STAGE2-WAVEA-02 | repair_loop | path helper naming mismatch on attempt 1 |
| STAGE2-WAVEA-03 | todo        |                                          |

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
* Codex starts sneaking task-planning behavior into Formam
* operator confidence drops below “I understand this diff”

Stopping is allowed.
Stopping is cheaper than smuggling confusion into the foundation.

---

## Suggested Commit Message Pattern

Use concise commit messages tied to the task.

Examples:

* `add formam storage module scaffolding`
* `add formam path constants and helpers`
* `add canonical deliverable normalization`
* `add markdown deliverable read write format`
* `add file backed deliverable reads and id allocation`
* `add formam parent goal validation helper`
* `add canonical goal map normalization`
* `add markdown goal map read write format`
* `add formam canonical write helpers`

This keeps history aligned with the task list.

---

## Definition Of Success For Wave A

Wave A succeeds when:

* all nine Wave A tasks are committed cleanly
* `azq/formam/storage.py` becomes the emerging storage authority for Formam
* deliverables and goal maps exist as visible, canonical file artifacts
* every deliverable can point back to a valid parent goal
* no task commands have been introduced
* the repo has a credible storage foundation for Stage 2 Wave B

Wave A is not the end of Stage 2.
It is the stone footing under Formam.

---

## Closing

This runbook is designed to keep Codex useful, bounded, and honest.

A good Stage 2 Wave A session should feel like careful joinery:

one beam,
one fit,
one check,
one brace.

Then the next beam.
