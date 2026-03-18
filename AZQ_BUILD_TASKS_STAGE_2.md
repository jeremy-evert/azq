# AZQ Build Tasks: Stage 2

## Purpose

This checklist turned **Stage 2: Implement Formam** from `AZQ_IMPLEMENTATION_PLAN.md` into atomic, commit-sized engineering work for the current repository.

The goal of Stage 2 is simple:

> introduce the form-building stage that turns goals into deliverables and dependency maps.

This checklist is intentionally grounded in the **current live tree**.
The repository does **not** currently use `src/azq/...`; the live code is under `azq/`.

The live Stage 2 baseline now includes:

* `azq/cli.py`
* `azq/formam/__init__.py`
* `azq/formam/storage.py`
* `azq/formam/build.py`
* `azq/formam/deliverables.py`
* `azq/formam/maps.py`
* `data/form/deliverables/`
* `data/form/maps/`

This checklist now serves as the Stage 2 completion ledger and reference for the canonical Formam baseline. It should still be practical enough to use while auditing the resulting code and artifacts.

---

## Stage 2 Outcome

Stage 2 is complete when canonical Formam artifacts exist on disk and the CLI can build, list, inspect, and map deliverables without introducing task-layer behavior.

At the end of Stage 2:

* each deliverable lives in its own file under `data/form/deliverables/`
* each goal map lives in its own file under `data/form/maps/`
* `azq form build <goal_id>` can create a stub deliverable and goal map for a valid parent goal
* `azq form list` can enumerate deliverables from canonical files
* `azq form show <deliverable_id>` can inspect one deliverable from canonical files
* `azq form map <goal_id>` can create or refresh a human-readable map artifact
* every deliverable points back to exactly one canonical goal
* no Agenda-style task creation is introduced before deliverables exist

That is the **visible structure layer** described in the implementation plan.

---

## Wave A Outcome

Wave A is complete when a canonical deliverable record and a canonical goal map record can exist as human-readable files, validated against canonical Finis goals, before command wiring is complete.

At the end of Wave A:

* `azq.formam.storage` exists and imports cleanly
* canonical deliverables can be written to and read from Markdown files
* canonical goal maps can be written to and read from Markdown files
* deliverables can be listed and inspected from file storage helpers alone
* next deliverable id generation is stable
* Formam can validate exact parent goals against canonical Finis storage before writing files
* no `azq form ...` CLI commands are required yet for the artifact model to exist

Wave A is intentionally a **storage foundation wave**, not a full working CLI wave.

---

## Canonical Stage 2 Baseline

The current implementation now establishes these Stage 2 truths:

* `azq/formam/` exists in the live repository
* canonical deliverables are stored one per file under `data/form/deliverables/`
* canonical goal maps are stored one per file under `data/form/maps/`
* the CLI exposes `azq form build`, `azq form list`, `azq form show`, and `azq form map`
* canonical deliverable and goal-map schema decisions live in code
* Formam validates parent goals against canonical Finis storage before writing deliverables
* the repository can truthfully reach `formed` from live artifacts on disk

For operators, `data/form/deliverables/` and `data/form/maps/` are the canonical Stage 2 system of record.
Those files are the first place to inspect when confirming what Formam currently believes.

---

## Canonical Stage 2 Deliverable Schema

Every canonical deliverable record should expose these fields:

* `deliverable_id`
* `goal_id`
* `title`
* `artifact_description`
* `dependencies`
* `status`
* `created`

Stage 2 rules:

* `goal_id` must resolve to an exact canonical `FINIS_###` goal
* `dependencies` is a list of deliverable ids and may be empty initially
* new deliverables begin as `drafted`
* `status` becomes `mapped` only after a goal map artifact exists
* deliverables describe artifacts and boundaries of work, not errands or task lists

This keeps Formam faithful to the charter: structure before execution.

---

## Canonical Stage 2 Map Schema

Every canonical goal map artifact should expose these fields:

* `goal_id`
* `deliverable_ids`
* `dependency_edges`
* `status`
* `created`
* `notes`

Stage 2 map rules:

* one goal map exists per goal as `data/form/maps/GOAL_<goal_id>_MAP.md`
* `deliverable_ids` must only reference deliverables for that exact parent goal
* `dependency_edges` must remain human-readable even if the file later gains machine-export support
* the first implementation may generate sparse or empty dependency sections, but the file must still be useful and inspectable

---

## Atomic Commit Checklist

### 1. Add Stage 2 storage contract notes

**Files:**

* `AZQ_BUILD_TASKS_STAGE_2.md`

**Work:**

* record the canonical Stage 2 deliverable schema
* record the canonical Stage 2 map schema
* record the canonical Stage 2 storage locations:

  * `data/form/deliverables/`
  * `data/form/maps/`
* state clearly that the live code is under `azq/`, not `src/azq/`
* state clearly that Wave A is a storage-foundation wave and does not yet require command wiring

**Definition of done:**

* the Stage 2 implementation target is explicit and repo-local

---

### 2. Create Formam package and storage scaffolding

**Files:**

* `azq/formam/__init__.py` (new)
* `azq/formam/storage.py` (new)

**Work:**

* create the new Formam package
* add a storage module that will own Formam path, schema, and persistence decisions
* keep the first commit limited to scaffolding and import-safe module boundaries

**Definition of done:**

* `azq.formam.storage` exists and imports cleanly

---

### 3. Add canonical Formam path constants and directory helpers

**Files:**

* `azq/formam/storage.py`

**Work:**

* define constants for:

  * `data/form/deliverables/`
  * `data/form/maps/`
* add helpers to:

  * ensure both directories exist
  * map a `deliverable_id` like `DELIV_001` to a Markdown file path
  * map a `goal_id` like `FINIS_001` to a map file path such as `GOAL_FINIS_001_MAP.md`
  * list deliverable files in stable order

**Definition of done:**

* one module owns all Formam storage path decisions

---

### 4. Define the canonical deliverable record model

**Files:**

* `azq/formam/storage.py`

**Work:**

* add normalization helpers that convert partial or generated deliverable data into the Stage 2 schema
* ensure every normalized record contains:

  * `deliverable_id`
  * `goal_id`
  * `title`
  * `artifact_description`
  * `dependencies`
  * `status`
  * `created`
* decide and document fallback behavior for missing generated fields:

  * missing `artifact_description`
  * missing `dependencies`
  * missing `created`
  * missing `status`

**Definition of done:**

* one function can take incomplete deliverable-shaped data and return a complete Stage 2 deliverable record

---

### 5. Implement deliverable file read/write format

**Files:**

* `azq/formam/storage.py`

**Work:**

* choose a diff-friendly on-disk format for `DELIV_###.md`
* implement serializer and parser helpers
* ensure each deliverable file is human-readable and preserves normalized fields clearly
* keep the format simple enough for later Agenda code to consume without transitional glue

**Definition of done:**

* a normalized deliverable can be written to and read from a single Markdown file without loss of required Stage 2 fields

---

### 6. Implement repository-level deliverable reads from file storage

**Files:**

* `azq/formam/storage.py`

**Work:**

* add functions to:

  * load all deliverables from `data/form/deliverables/`
  * load one deliverable by exact `deliverable_id`
  * load all deliverables for one exact `goal_id`
  * compute the next stable `DELIV_###` id from existing file-based deliverables
* ensure sort order is deterministic
* ensure lookup is exact-match only on ids

**Definition of done:**

* file storage alone can support deliverable listing, lookup, goal grouping, and id allocation

---

### 7. Add canonical goal-parent validation helpers

**Files:**

* `azq/formam/storage.py`

**Work:**

* add helpers that validate a parent goal against canonical Finis storage
* require exact `goal_id` lookup
* reject missing parent goals before any deliverable is written
* reject non-active parent goals if the implementation chooses to enforce active-only form building at this stage
* keep goal validation logic close to Formam storage rather than scattering it through CLI handlers

**Definition of done:**

* Formam can prove that a deliverable descends from a real canonical goal before writing files

---

### 8. Define the canonical goal-map model

**Files:**

* `azq/formam/storage.py`

**Work:**

* define the canonical map filename convention for `GOAL_<goal_id>_MAP.md`
* add normalization helpers for goal map records
* define the minimal Stage 2 map fields:

  * `goal_id`
  * `deliverable_ids`
  * `dependency_edges`
  * `status`
  * `created`
  * `notes`

**Definition of done:**

* one function can take partial map-shaped data and return a complete canonical goal map record

---

### 9. Implement goal-map file read/write format

**Files:**

* `azq/formam/storage.py`

**Work:**

* choose a diff-friendly Markdown format for goal maps
* implement serializer and parser helpers
* keep dependency sections human-readable first
* ensure map files can round-trip without losing required fields

**Definition of done:**

* one canonical goal map can be written to and read from a Markdown file without loss of required Stage 2 fields

---

### 10. Add canonical Formam write helpers

**Files:**

* `azq/formam/storage.py`
* `data/form/deliverables/`
* `data/form/maps/`

**Work:**

* add a canonical single-record write helper for deliverables
* add a canonical write helper for goal maps
* ensure each helper writes exactly one canonical file in the correct directory
* keep the write-side boundary in `azq/formam/storage.py`

**Definition of done:**

* callers can persist one normalized deliverable and one normalized goal map without making path or format decisions elsewhere

---

### 11. Implement `azq form build <goal_id>`

**Files:**

* `azq/formam/build.py` (new)
* `azq/formam/storage.py`

**Work:**

* load and validate the parent goal by exact `goal_id`
* allocate a new `DELIV_###` id
* generate a stub deliverable record for that goal
* write the canonical deliverable file
* generate or refresh the canonical goal map file for that goal
* keep the first implementation intentionally small and inspectable rather than trying to solve full planning automatically

**Definition of done:**

* one valid active goal can produce at least one canonical deliverable file and one canonical goal map file

---

### 12. Implement `azq form list`

**Files:**

* `azq/formam/deliverables.py` (new)
* `azq/formam/storage.py`

**Work:**

* add a read-only listing function for canonical deliverables
* display at least:

  * `deliverable_id`
  * `goal_id`
  * `title`
  * `status`
* preserve the distinction between “no deliverables exist” and “deliverables exist but none match a requested filter” if filters are added later

**Definition of done:**

* `azq form list` can inspect Formam output without mutating state

---

### 13. Implement `azq form show <deliverable_id>`

**Files:**

* `azq/formam/deliverables.py`
* `azq/formam/storage.py`

**Work:**

* load one deliverable by exact `deliverable_id`
* print the canonical fields clearly
* keep the output centered on artifact definition and dependencies rather than task speculation

**Definition of done:**

* one canonical deliverable can be inspected from the CLI by exact id

---

### 14. Implement `azq form map <goal_id>`

**Files:**

* `azq/formam/maps.py` (new)
* `azq/formam/storage.py`

**Work:**

* load and validate the parent goal by exact `goal_id`
* load all deliverables for that goal
* generate or refresh the canonical goal map file
* keep the first implementation human-readable and conservative even if dependency data is sparse

**Definition of done:**

* a goal with deliverables can produce a visible map artifact under `data/form/maps/`

---

### 15. Wire Formam commands into the CLI

**Files:**

* `azq/cli.py`

**Work:**

* add command help for:

  * `azq form build <goal_id>`
  * `azq form list`
  * `azq form show <deliverable_id>`
  * `azq form map <goal_id>`
* route those commands to the new Formam modules
* keep command handling narrow and consistent with the existing CLI style

**Definition of done:**

* the CLI exposes the first usable Formam loop

---

### 16. Add regression tests for Stage 2 structure behavior

**Files:**

* `tests/` or `tests/fixtures/`

**Work:**

* add tests for:

  * deliverable normalization
  * deliverable Markdown round-trip read/write
  * next deliverable id generation from file-backed deliverables
  * exact parent-goal validation
  * goal-map Markdown round-trip read/write
  * `form build` writing a canonical deliverable and canonical goal map
  * `form list` reading canonical deliverables
  * `form show` loading one canonical deliverable
  * `form map` writing a canonical goal map
* keep tests focused on structure invariants and CLI-visible behavior

**Definition of done:**

* Stage 2 behavior is locked by tests rather than manual inspection alone

---

### 17. Update repo docs that Stage 2 changes will invalidate

**Files:**

* `AZQ_BOOTSTRAP.md`
* `README.md`
* any Formam-specific notes

**Work:**

* update docs that still present Formam as doctrine only
* define `data/form/deliverables/` and `data/form/maps/` as active Formam storage
* clarify that deliverables come before tasks
* align examples with canonical `DELIV_###` and `GOAL_<goal_id>_MAP.md` artifacts

**Definition of done:**

* the docs teach the live Stage 2 Formam model rather than only the planned one

**Stage 2 closeout note:**

* this documentation alignment belongs to Wave C because Formam is no longer aspirational at Stage 2
* operator-facing docs should describe the file-backed baseline as already live, not merely planned

---

## Commit Grouping Suggestion

If you want these as sensible commit waves rather than 17 single-file nibbles, use this grouping:

### Wave A — Storage foundation

* tasks 2–10

### Wave B — Command implementation

* tasks 11–15

### Wave C — Evidence and closeout

* tasks 16–17

This keeps each wave reviewable while still respecting atomicity.

Wave A is intentionally broader than the old Stage 1 storage wave because Formam needs both deliverable and map artifact models defined before the CLI can safely create either one.

Wave C closes Stage 2 by making the documentation match that live baseline, explicitly teaching operators that `data/form/deliverables/` and `data/form/maps/` are the canonical records to inspect.

---

## Stage 2 Exit Audit

Stage 2 is done when all of the following are true:

* each deliverable is stored as one `DELIV_###.md` file
* each goal map is stored as one `GOAL_<goal_id>_MAP.md` file
* `azq form build <goal_id>` writes only canonical file-backed Formam artifacts
* `azq form list` reads from canonical Formam storage
* `azq form show <deliverable_id>` reads from canonical Formam storage
* `azq form map <goal_id>` writes only canonical file-backed Formam artifacts
* every deliverable points back to a valid canonical goal
* deliverable records expose `deliverable_id`, `goal_id`, `title`, `artifact_description`, `dependencies`, `status`, and `created`
* goal map records expose `goal_id`, `deliverable_ids`, `dependency_edges`, `status`, `created`, and `notes`
* the resulting files are readable and diff-friendly
* no task commands are introduced before deliverables exist
* later Agenda code can resolve deliverables from filesystem records without hidden planning state
* the repository can truthfully reach `formed` from visible files

---

## Closing

Stage 2 is where AZQ either keeps its craft order or starts to collapse into generic project management.

Do Formam carefully, and Agenda will inherit structure instead of chaos.
