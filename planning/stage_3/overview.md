# AZQ Build Tasks: Stage 3

## Purpose

This checklist records the atomic, commit-sized engineering work that established the live Stage 3 Agenda baseline in the current repository.

The goal of Stage 3 is simple:

> turn canonical deliverables into executable tasks with visible dependency order and durable work logs.

This checklist is grounded in the **current live repository**, not an older imagined baseline.
The live code is under `azq/`, not `src/azq/...`.

The current baseline now includes:

* canonical Finis goal storage under `data/finis/goals/`
* canonical Formam deliverable storage under `data/form/deliverables/`
* canonical Formam goal maps under `data/form/maps/`
* canonical Agenda task storage under `data/agenda/tasks/`
* canonical Agenda DAG storage under `data/agenda/dags/`
* canonical Agenda task-log storage under `data/agenda/logs/`
* a split CLI routed through engine-specific command layers, including the live `azq agenda` command family

That means Stage 3 no longer needs to be described as a future-only design target.
Agenda is now the visible craft layer on top of live Stage 1 and Stage 2 storage, and this document should read as an implementation record and closeout reference rather than a speculative rewrite.

---

## Stage 3 Outcome

Stage 3 is complete when canonical Agenda artifacts exist on disk and the current CLI can build and inspect them through the live `azq agenda` command family without bypassing the deliverable layer.

At the end of Stage 3:

* each task lives in its own file under `data/agenda/tasks/`
* each goal-level task graph lives in its own file under `data/agenda/dags/`
* each task log lives under `data/agenda/logs/` as durable Stage 3 work evidence
* `azq agenda build <deliverable_id>` can derive an initial executable structure from one canonical deliverable
* `azq agenda list` can enumerate canonical tasks from file storage
* `azq agenda show <task_id>` can inspect one canonical task
* `azq agenda dag <deliverable_id>` can refresh and inspect the current goal-level DAG artifact for that deliverable's parent goal
* every task points back to exactly one canonical deliverable

Stage 3 stops at the **actionable** layer.

It does **not** introduce:

* artifact publication
* archive engine behavior
* repo-wide doctor/status theatrics
* premature Stage 4 or Stage 5 concerns

The job here is not to make Agenda clever.
The job is to make the work graph real.

---

## Current Stage 3 Gaps

The live implementation no longer has the original Stage 3 gaps.
The remaining closeout gaps are documentation and framing gaps:

* some older docs still describe Agenda as future-only work
* some older docs still describe the outdated `azq task ...` and `azq dag ...` command split rather than the live `azq agenda ...` family
* some older docs still frame DAG commands around a direct `goal_id` CLI surface even though the current operator path is `azq agenda build <deliverable_id>` and `azq agenda dag <deliverable_id>`
* some older docs still imply `task start` and `task complete` are live Stage 3 commands even though that behavior is not exposed by the current CLI
* Stage 3 closeout must keep teaching `data/agenda/tasks/`, `data/agenda/dags/`, and `data/agenda/logs/` as the canonical system of record

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
* the first implementation may generate **sparse** graphs and stub tasks
* `agenda build` should prefer visible, inspectable correctness over clever planning

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

* `planning/stage_3/overview.md`

**Work:**

* record the canonical Stage 3 task schema
* record the canonical Stage 3 DAG schema
* record the canonical Stage 3 task-log model
* record the canonical Stage 3 storage locations:

  * `data/agenda/tasks/`
  * `data/agenda/dags/`
  * `data/agenda/logs/`
* state clearly that Stage 3 builds on already-live Finis and Formam storage
* state clearly that Stage 3 stops at the actionable layer

**Definition of done:**

* the Stage 3 implementation target is explicit and repo-local

---

### 2. Create Agenda package scaffolding

**Files:**

* `azq/agenda/__init__.py` (new)
* `azq/agenda/storage.py` (new)

**Work:**

* create the new Agenda package
* add a storage facade module for Stage 3
* keep the first commit limited to scaffolding and import-safe module boundaries

**Definition of done:**

* `azq.agenda.storage` exists and imports cleanly

---

### 3. Extract Agenda path and directory helpers into focused modules

**Files:**

* `azq/agenda/paths.py` (new)
* `azq/agenda/storage.py`

**Work:**

* define constants for:

  * `data/agenda/tasks/`
  * `data/agenda/dags/`
  * `data/agenda/logs/`
* add helpers to:

  * ensure all three directories exist
  * map a `task_id` like `TASK_001` to a task file path
  * map a `goal_id` like `FINIS_001` to a DAG file path
  * map a `task_id` like `TASK_001` to a log file path
  * list task files in stable order
* keep path ownership out of general storage logic

**Definition of done:**

* one focused module owns all Agenda path decisions

---

### 4. Extract canonical task schema helpers into a focused module

**Files:**

* `azq/agenda/schemas.py` (new)
* `azq/agenda/storage.py`

**Work:**

* add normalization helpers that convert partial or generated task data into the Stage 3 task schema
* ensure every normalized task record contains:

  * `task_id`
  * `deliverable_id`
  * `description`
  * `dependencies`
  * `status`
  * `execution_notes`
  * `created`
* decide and document fallback behavior for missing generated fields

**Definition of done:**

* one focused module can normalize incomplete task-shaped data into canonical task records

---

### 5. Implement task storage helpers in a dedicated task-storage module

**Files:**

* `azq/agenda/task_storage.py` (new)
* `azq/agenda/storage.py`

**Work:**

* choose a diff-friendly on-disk format for `TASK_###.md`
* implement serializer and parser helpers
* add repository helpers to:

  * load all tasks
  * load one task by exact `task_id`
  * load all tasks for one exact `deliverable_id`
  * compute the next stable `TASK_###` id from existing file-backed tasks
* ensure sort order is deterministic
* ensure lookup is exact-match only

**Definition of done:**

* task records can be normalized, written, read, listed, and allocated without bloating the storage facade

---

### 6. Add canonical deliverable-parent validation helpers

**Files:**

* `azq/agenda/task_storage.py`
* possibly `azq/formam/storage.py`

**Work:**

* add a validation helper that loads one canonical deliverable by exact `deliverable_id`
* fail clearly when the parent deliverable is missing
* fail clearly when a deliverable record is malformed enough that task derivation should stop
* keep the validation helper small and reusable by later Agenda commands

**Definition of done:**

* Stage 3 has one exact-match deliverable validation boundary before tasks are created or mutated

---

### 7. Extract canonical DAG schema helpers into a focused module

**Files:**

* `azq/agenda/schemas.py`
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

* one focused module can normalize incomplete DAG-shaped data into canonical DAG records

---

### 8. Implement DAG storage helpers in a dedicated DAG-storage module

**Files:**

* `azq/agenda/dag_storage.py` (new)
* `azq/agenda/storage.py`

**Work:**

* choose a simple, inspectable on-disk JSON format for `GOAL_<goal_id>_DAG.json`
* implement serializer and parser helpers
* add repository helpers to:

  * load one DAG by exact `goal_id`
  * write one canonical DAG record
  * derive stable dependency-edge structures from task relationships
* keep dependency-edge derivation beside DAG logic rather than burying it in a generic facade

**Definition of done:**

* DAG records can be normalized, written, read, and inspected without turning `storage.py` into a grab bag

---

### 9. Implement task-log helpers in a dedicated log-storage module

**Files:**

* `azq/agenda/log_storage.py` (new)
* `azq/agenda/storage.py`

**Work:**

* add helpers to:

  * create one task log file for a canonical task
  * append a visible `started` entry
  * append a visible `completed` entry
* keep the log format human-readable and append-only
* keep log writing separate from later artifact publication logic

**Definition of done:**

* Stage 3 can leave durable work-log evidence without introducing later artifact or archive behavior

---

### 10. Keep `azq/agenda/storage.py` as a thin facade

**Files:**

* `azq/agenda/storage.py`

**Work:**

* re-export the public Agenda storage helpers from the focused modules
* keep the facade readable and stable for the command layer
* avoid recreating a monolithic storage file that will need Wave D surgery later

**Definition of done:**

* `azq/agenda/storage.py` is the public boundary, not the implementation blob

---

### 11. Implement `azq agenda build <deliverable_id>`

**Files:**

* `azq/agenda/dags.py` (new)
* `azq/agenda/task_storage.py`
* `azq/agenda/dag_storage.py`

**Work:**

* validate the parent deliverable by exact `deliverable_id`
* load the canonical deliverable from Formam storage
* generate one or more initial canonical tasks for that deliverable
* derive or refresh the visible parent-goal DAG conservatively from the deliverable task relationships
* allow the first implementation to generate sparse task sets and sparse graphs when certainty is low
* write the resulting canonical task files
* write the resulting canonical DAG file

**Definition of done:**

* a deliverable can produce visible Stage 3 task artifacts and refresh the parent goal DAG under `data/agenda/`

---

### 12. Implement `azq agenda dag <deliverable_id>`

**Files:**

* `azq/agenda/dags.py`

**Work:**

* validate one canonical deliverable by exact `deliverable_id`
* load or refresh the parent goal DAG artifact from canonical storage
* print the durable DAG path clearly for terminal inspection
* fail clearly when the parent deliverable does not exist

**Definition of done:**

* one goal-level DAG can be refreshed and inspected from the command layer through the live deliverable-scoped operator path

---

### 13. Implement `azq agenda list`

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

### 14. Implement `azq agenda show <task_id>`

**Files:**

* `azq/agenda/tasks.py`

**Work:**

* load one canonical task by exact `task_id`
* print the task fields clearly for terminal inspection
* keep the output narrow, readable, and faithful to the canonical task record
* fail clearly when the task file does not exist

**Definition of done:**

* one canonical task can be inspected from the live command layer without mutating state

---

### 15. Preserve canonical task-log artifacts as on-disk Stage 3 evidence

**Files:**

* `azq/agenda/log_storage.py`

**Work:**

* keep the log format append-only and human-readable
* ensure task-log helpers keep writing under `data/agenda/logs/`
* keep task-log evidence on disk even though the current operator surface does not expose `task start` or `task complete`
* avoid coupling task logs to later artifact-publication or archive behavior

**Definition of done:**

* Stage 3 preserves durable log evidence on disk without teaching a wider live CLI surface than the repository actually exposes

---

### 16. Wire Agenda commands into the CLI

**Files:**

* `azq/agenda/cli.py` (new)
* `azq/agenda/router.py` (new)
* `azq/cli.py`

**Work:**

* add command help for:

  * `azq agenda build <deliverable_id>`
  * `azq agenda list`
  * `azq agenda show <task_id>`
  * `azq agenda dag <deliverable_id>`
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
  * `agenda build` writing canonical tasks and a canonical DAG
  * `agenda dag` refreshing and loading one canonical DAG through an exact `deliverable_id`
  * `agenda list` reading canonical tasks
  * `agenda show` reading one canonical task
* keep tests focused on structure invariants and CLI-visible behavior

**Definition of done:**

* Stage 3 behavior is locked by tests rather than manual inspection alone

---

### 18. Update repo docs that Stage 3 changes will invalidate

**Files:**

* `docs/architecture/AZQ_BOOTSTRAP.md`
* `README.md`
* any Agenda-specific notes

**Work:**

* update docs that still present Agenda as doctrine only
* define `data/agenda/tasks/`, `data/agenda/dags/`, and `data/agenda/logs/` as active Agenda storage
* clarify that tasks descend from deliverables rather than replacing them
* align examples with canonical `TASK_###`, `GOAL_<goal_id>_DAG.json`, and `TASK_###_LOG.md` artifacts
* clarify that task logs provide durable work evidence before any later-stage publication behavior exists

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
But it is also intentionally **pre-split** so path logic, schema logic, task storage, DAG storage, and log storage do not collapse into one swollen `storage.py`.

Wave B stays narrow by focusing only on the first executable loop:

* derive a DAG from visible deliverables
* inspect the DAG through the live `agenda` surface
* list tasks
* inspect one task

Wave C closes Stage 3 by turning the live Agenda behavior into a tested and documented baseline before later artifact, archive, status, and doctor work arrives.

---

## Stage 3 Exit Audit

Stage 3 is done when all of the following are true:

* each task is stored as one `TASK_###.md` file
* each goal-level DAG is stored as one `GOAL_<goal_id>_DAG.json` file
* each task log is stored under `data/agenda/logs/` as durable Stage 3 work evidence
* `azq agenda build <deliverable_id>` writes only canonical file-backed Agenda artifacts
* `azq agenda dag <deliverable_id>` reads and refreshes canonical Agenda DAG storage
* `azq agenda list` reads from canonical Agenda storage
* `azq agenda show <task_id>` reads one canonical task from canonical Agenda storage
* every task points back to a valid canonical deliverable
* task records expose `task_id`, `deliverable_id`, `description`, `dependencies`, `status`, `execution_notes`, and `created`
* DAG records expose `goal_id`, `deliverable_ids`, `task_ids`, `dependency_edges`, `status`, `created`, and `notes`
* the resulting files are readable, diff-friendly, and inspectable without hidden state
* no artifact publication or archive commands are introduced before the later stages
* the trace chain `task -> deliverable -> goal` is machine-checkable and human-readable
* the repository can truthfully reach `actionable` from visible files

---

## Closing

Stage 3 is where AZQ turns deliverable structure into visible executable work.

Do it carefully and you get a real action layer.
Do it carelessly and you get a task manager wearing a philosopher’s coat.

Agenda should not be clever first.
It should be legible, file-backed, and true.
