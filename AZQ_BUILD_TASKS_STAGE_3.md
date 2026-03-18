# AZQ Build Tasks: Stage 3

## Purpose

This checklist turns **Stage 3: Implement Agenda** from `AZQ_IMPLEMENTATION_PLAN.md` into atomic, commit-sized engineering work for the current repository.

The goal of Stage 3 is simple:

> turn canonical deliverables into executable tasks with visible dependency order and durable work logs.

This checklist is intentionally grounded in the **current live tree**.
The repository does **not** currently use `src/azq/...`; the live code is under `azq/`.

The live Stage 3 baseline now includes:

* `azq/cli.py` as a thin top-level dispatcher
* `azq/scintilla/cli.py`
* `azq/finis/cli.py`
* `azq/formam/cli.py`
* `azq/formam/deliverable_storage.py`
* `azq/formam/map_storage.py`
* `azq/formam/paths.py`
* `azq/formam/schemas.py`
* `data/finis/goals/`
* `data/form/deliverables/`
* `data/form/maps/`

This checklist therefore starts from a repo where Stage 1 and Stage 2 are already live.
It should still be practical enough to use while actually committing Stage 3 work.

**Stage 3 planning note:**

* `AZQ_IMPLEMENTATION_PLAN.md` still describes an older baseline where Formam is not yet implemented and recommended paths still use `src/azq/...`
* this checklist favors the live repository reality instead:

  * Stage 1 Finis storage is already canonical and file-backed
  * Stage 2 Formam storage and commands are already canonical and file-backed
  * the top-level CLI is already split through engine-specific routers

---

## Stage 3 Outcome

Stage 3 is complete when canonical Agenda artifacts exist on disk and the CLI can build, inspect, start, and complete tasks without bypassing the deliverable layer or introducing artifact/archive behavior early.

At the end of Stage 3:

* each task lives in its own file under `data/agenda/tasks/`
* each goal-level task graph lives in its own file under `data/agenda/dags/`
* each started or completed task leaves durable log evidence under `data/agenda/logs/`
* `azq dag build <goal_id>` can derive an initial executable structure from canonical deliverables
* `azq dag show <goal_id>` can inspect one goal-level task graph
* `azq task list` can enumerate canonical tasks from file storage
* `azq task start <task_id>` can transition one canonical task into active work and write a log entry
* `azq task complete <task_id>` can transition one canonical task to completion and write a log entry
* every task points back to exactly one canonical deliverable
* no artifact publication, archive behavior, or repository-wide doctor/status behavior is introduced before the later stages

That is the **action layer** described in the implementation plan and the state model.

---

## Current Stage 3 Gaps

The current implementation has these concrete mismatches with the Stage 3 objective:

* no `azq/agenda/` package exists in the live repository
* no `data/agenda/tasks/` directory exists
* no `data/agenda/dags/` directory exists
* no `data/agenda/logs/` directory exists
* the CLI exposes no `azq task ...` or `azq dag ...` commands yet
* no canonical task schema exists in code
* no canonical DAG schema exists in code
* no durable task-log format exists in code
* no task can currently prove a valid deliverable parent
* the repository can truthfully reach `formed`, but not yet `actionable`, from visible artifacts alone

---

## Canonical Stage 3 Task Schema

Every canonical task record should expose these fields:

* `task_id`
* `deliverable_id`
* `description`
* `dependencies`
* `status`
* `execution_notes`
* `created`

Stage 3 task rules:

* `deliverable_id` must resolve to an exact canonical `DELIV_###` deliverable
* `dependencies` is a list of task ids and may be empty initially
* new tasks begin as `ready`
* `execution_notes` is a visible text field and may be empty until work starts
* tasks describe executable work units in service of one deliverable, not free-floating errands

This keeps Agenda subordinate to Formam rather than replacing it.

---

## Canonical Stage 3 DAG Schema

Every canonical goal-level DAG artifact should expose these fields:

* `goal_id`
* `deliverable_ids`
* `task_ids`
* `dependency_edges`
* `status`
* `created`
* `notes`

Stage 3 DAG rules:

* one DAG exists per goal as `data/agenda/dags/GOAL_<goal_id>_DAG.json`
* `deliverable_ids` must only reference deliverables for that exact parent goal
* `task_ids` must only reference canonical tasks descended from those deliverables
* `dependency_edges` must remain inspectable and deterministic
* the first implementation may generate sparse graphs, but the resulting file must still be useful to a human operator

This keeps the first Agenda graph visible rather than magical.

---

## Canonical Stage 3 Task Log Model

Every canonical task log artifact should expose durable evidence of state transitions for one task.

Stage 3 log rules:

* one task log exists per task as `data/agenda/logs/<task_id>_LOG.md`
* log entries are append-only within the first implementation
* starting work writes a visible `started` entry
* completing work writes a visible `completed` entry
* logs record what happened, not just the resulting status
* task completion does not imply artifact publication automatically

This keeps work evidence inspectable before later artifact and archive layers exist.

---

## Atomic Commit Checklist

### 1. Add Stage 3 storage contract notes

**Files:**

* `AZQ_BUILD_TASKS_STAGE_3.md`

**Work:**

* record the canonical Stage 3 task schema
* record the canonical Stage 3 DAG schema
* record the canonical Stage 3 task-log model
* record the canonical Stage 3 storage locations:

  * `data/agenda/tasks/`
  * `data/agenda/dags/`
  * `data/agenda/logs/`
* state clearly that the live code is under `azq/`, not `src/azq/`
* state clearly that Stage 3 builds on already-live Finis and Formam storage rather than reopening them

**Definition of done:**

* the Stage 3 implementation target is explicit and repo-local

---

### 2. Create Agenda package and storage scaffolding

**Files:**

* `azq/agenda/__init__.py` (new)
* `azq/agenda/storage.py` (new)

**Work:**

* create the new Agenda package
* add a storage module that will own Agenda path, schema, and persistence decisions
* keep the first commit limited to scaffolding and import-safe module boundaries

**Definition of done:**

* `azq.agenda.storage` exists and imports cleanly

---

### 3. Add canonical Agenda path constants and directory helpers

**Files:**

* `azq/agenda/storage.py`

**Work:**

* define constants for:

  * `data/agenda/tasks/`
  * `data/agenda/dags/`
  * `data/agenda/logs/`
* add helpers to:

  * ensure all three directories exist
  * map a `task_id` like `TASK_001` to a Markdown file path
  * map a `goal_id` like `FINIS_001` to a DAG file path such as `GOAL_FINIS_001_DAG.json`
  * map a `task_id` like `TASK_001` to a log file path such as `TASK_001_LOG.md`
  * list task files in stable order

**Definition of done:**

* one module owns all Agenda storage path decisions

---

### 4. Define the canonical task record model

**Files:**

* `azq/agenda/storage.py`

**Work:**

* add normalization helpers that convert partial or generated task data into the Stage 3 schema
* ensure every normalized record contains:

  * `task_id`
  * `deliverable_id`
  * `description`
  * `dependencies`
  * `status`
  * `execution_notes`
  * `created`
* decide and document fallback behavior for missing generated fields:

  * missing `dependencies`
  * missing `status`
  * missing `execution_notes`
  * missing `created`

**Definition of done:**

* one function can take incomplete task-shaped data and return a complete Stage 3 task record

---

### 5. Implement task file read/write format

**Files:**

* `azq/agenda/storage.py`

**Work:**

* choose a diff-friendly on-disk format for `TASK_###.md`
* implement serializer and parser helpers
* ensure each task file is human-readable and preserves normalized fields clearly
* keep the format simple enough for later artifact and archive code to consume without transitional glue

**Definition of done:**

* a normalized task can be written to and read from a single Markdown file without loss of required Stage 3 fields

---

### 6. Implement repository-level task reads from file storage

**Files:**

* `azq/agenda/storage.py`

**Work:**

* add functions to:

  * load all tasks from `data/agenda/tasks/`
  * load one task by exact `task_id`
  * load all tasks for one exact `deliverable_id`
  * compute the next stable `TASK_###` id from existing file-based tasks
* ensure sort order is deterministic
* ensure lookup is exact-match only on `task_id` and `deliverable_id`

**Definition of done:**

* file storage alone can support task listing, exact lookup, and id allocation

---

### 7. Add canonical deliverable-parent validation helpers

**Files:**

* `azq/agenda/storage.py`
* possibly `azq/formam/storage.py`

**Work:**

* add a validation helper that loads one canonical deliverable by exact `deliverable_id`
* fail clearly when the parent deliverable is missing
* fail clearly when a deliverable record is malformed enough that task derivation should stop
* keep the validation helper small and reusable by later Agenda commands

**Definition of done:**

* Stage 3 has one exact-match deliverable validation boundary before tasks are created or mutated

---

### 8. Define the canonical DAG record model

**Files:**

* `azq/agenda/storage.py`

**Work:**

* add normalization helpers that convert partial DAG-shaped data into the Stage 3 DAG schema
* ensure every normalized DAG record contains:

  * `goal_id`
  * `deliverable_ids`
  * `task_ids`
  * `dependency_edges`
  * `status`
  * `created`
  * `notes`
* decide and document fallback behavior for missing generated fields

**Definition of done:**

* one function can take incomplete DAG-shaped data and return a complete Stage 3 DAG record

---

### 9. Implement DAG file read/write format

**Files:**

* `azq/agenda/storage.py`

**Work:**

* choose a simple, inspectable on-disk JSON format for `GOAL_<goal_id>_DAG.json`
* implement serializer and parser helpers
* ensure the file preserves normalized DAG fields clearly
* keep the resulting JSON simple enough for humans to inspect and later code to extend

**Definition of done:**

* a normalized DAG record can be written to and read from one JSON file without loss of required Stage 3 fields

---

### 10. Add canonical task-log write helpers

**Files:**

* `azq/agenda/storage.py`

**Work:**

* add helpers to:

  * create one task log file for a canonical task
  * append a visible `started` entry
  * append a visible `completed` entry
* keep the log format human-readable and append-only in the first implementation
* keep log writing separate from later artifact publication logic

**Definition of done:**

* Stage 3 can leave durable work-log evidence without introducing Stage 4 archive behavior

---

### 11. Implement `azq dag build <goal_id>`

**Files:**

* `azq/agenda/dags.py` (new)
* `azq/agenda/storage.py`

**Work:**

* validate the parent goal by exact `goal_id`
* load canonical deliverables for that exact goal from Formam storage
* generate one or more initial canonical tasks for those deliverables
* derive a first visible dependency graph conservatively from deliverable relationships
* write the resulting canonical task files
* write the resulting canonical DAG file
* keep the first implementation inspectable and conservative rather than “smart”

**Definition of done:**

* a goal with deliverables can produce visible Stage 3 task and DAG artifacts under `data/agenda/`

---

### 12. Implement `azq dag show <goal_id>`

**Files:**

* `azq/agenda/dags.py`

**Work:**

* load one canonical DAG by exact `goal_id`
* print the DAG fields clearly for terminal inspection
* keep the output centered on task order and dependency structure
* fail clearly when the DAG file does not exist

**Definition of done:**

* one goal-level DAG can be inspected from the command layer by exact parent goal id

---

### 13. Implement `azq task list`

**Files:**

* `azq/agenda/tasks.py` (new)

**Work:**

* add a read-only task listing over canonical Agenda storage
* display at least:

  * `task_id`
  * `deliverable_id`
  * `status`
  * short description
* preserve a clear no-tasks message when canonical storage is empty

**Definition of done:**

* canonical tasks can be listed without mutating state

---

### 14. Implement `azq task start <task_id>`

**Files:**

* `azq/agenda/tasks.py`
* `azq/agenda/storage.py`

**Work:**

* load one canonical task by exact `task_id`
* rewrite only that task file with a started status such as `in_progress`
* append a visible `started` log entry under `data/agenda/logs/`
* keep the transition narrow and inspectable
* do not publish artifacts or archive anything in this task

**Definition of done:**

* starting one task updates canonical task state and leaves durable log evidence

---

### 15. Implement `azq task complete <task_id>`

**Files:**

* `azq/agenda/tasks.py`
* `azq/agenda/storage.py`

**Work:**

* load one canonical task by exact `task_id`
* rewrite only that task file with a completed status
* append a visible `completed` log entry under `data/agenda/logs/`
* keep the transition narrow and inspectable
* do not publish artifacts or archive anything in this task

**Definition of done:**

* completing one task updates canonical task state and leaves durable log evidence

---

### 16. Wire Agenda commands into the CLI

**Files:**

* `azq/agenda/cli.py` (new)
* `azq/agenda/router.py` (new)
* `azq/cli.py`

**Work:**

* add command help for:

  * `azq task list`
  * `azq task start <task_id>`
  * `azq task complete <task_id>`
  * `azq dag build <goal_id>`
  * `azq dag show <goal_id>`
* route those commands through the same engine-router style already used by Scintilla, Finis, and Formam
* keep command handling narrow and consistent with the live CLI style

**Definition of done:**

* the CLI exposes the first usable Agenda loop

---

### 17. Add regression tests for Stage 3 action behavior

**Files:**

* `tests/` or `tests/fixtures/`

**Work:**

* add tests for:

  * task normalization
  * task Markdown round-trip read/write
  * next task id generation from file-backed tasks
  * exact deliverable-parent validation
  * DAG JSON round-trip read/write
  * task-log append helpers
  * `dag build` writing canonical tasks and a canonical DAG
  * `dag show` loading one canonical DAG
  * `task list` reading canonical tasks
  * `task start` updating task state and writing a log entry
  * `task complete` updating task state and writing a log entry
* keep tests focused on structure invariants and CLI-visible behavior

**Definition of done:**

* Stage 3 behavior is locked by tests rather than manual inspection alone

---

### 18. Update repo docs that Stage 3 changes will invalidate

**Files:**

* `AZQ_BOOTSTRAP.md`
* `README.md`
* any Agenda-specific notes

**Work:**

* update docs that still present Agenda as doctrine only
* define `data/agenda/tasks/`, `data/agenda/dags/`, and `data/agenda/logs/` as active Agenda storage
* clarify that tasks descend from deliverables rather than replacing them
* align examples with canonical `TASK_###` and `GOAL_<goal_id>_DAG.json` artifacts
* clarify that task logs provide durable work evidence before artifact publication exists

**Definition of done:**

* the docs teach the live Stage 3 Agenda model rather than only the planned one

**Stage 3 closeout note:**

* this documentation alignment belongs to the closeout wave because Agenda should be visibly real before operator-facing docs teach it as active baseline

---

## Commit Grouping Suggestion

If you want these as sensible commit waves rather than 18 single-file nibbles, use this grouping:

### Wave A — Agenda storage foundation

* tasks 2–10

### Wave B — Command implementation

* tasks 11–16

### Wave C — Evidence and closeout

* tasks 17–18

This keeps each wave reviewable while still respecting atomicity.

Wave A is intentionally broad because Agenda needs task records, DAG records, log records, and exact deliverable validation in place before command wiring can safely create or mutate anything.

Wave B stays narrow by focusing only on the first executable loop:

* derive a DAG from visible deliverables
* inspect the DAG
* list tasks
* start tasks
* complete tasks

Wave C closes Stage 3 by turning the live Agenda behavior into a tested and documented baseline before later artifact, archive, status, and doctor work arrives.

---

## Stage 3 Exit Audit

Stage 3 is done when all of the following are true:

* each task is stored as one `TASK_###.md` file
* each goal-level DAG is stored as one `GOAL_<goal_id>_DAG.json` file
* each started or completed task has durable log evidence under `data/agenda/logs/`
* `azq dag build <goal_id>` writes only canonical file-backed Agenda artifacts
* `azq dag show <goal_id>` reads from canonical Agenda storage
* `azq task list` reads from canonical Agenda storage
* `azq task start <task_id>` rewrites one canonical task file and appends one canonical log entry
* `azq task complete <task_id>` rewrites one canonical task file and appends one canonical log entry
* every task points back to a valid canonical deliverable
* task records expose `task_id`, `deliverable_id`, `description`, `dependencies`, `status`, `execution_notes`, and `created`
* DAG records expose `goal_id`, `deliverable_ids`, `task_ids`, `dependency_edges`, `status`, `created`, and `notes`
* the resulting files are readable, diff-friendly, and inspectable without hidden state
* no artifact publication or archive commands are introduced before the later stages
* the trace chain `task -> deliverable -> goal` is machine-checkable and human-readable
* the repository can truthfully reach `actionable` from visible files

---

## Closing
