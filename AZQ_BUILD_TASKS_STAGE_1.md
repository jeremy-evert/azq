# AZQ Build Tasks: Stage 1

## Purpose

This checklist turns **Stage 1: Normalize Finis Storage** from `AZQ_IMPLEMENTATION_PLAN.md` into atomic, commit-sized engineering work for the current repository.

The goal of Stage 1 is simple:

> move Finis from transitional JSON storage to first-class goal files so the on-disk structure matches the filesystem and state models.

This checklist is intentionally grounded in the **current live tree**.
The repository does **not** currently use `src/azq/...`; the live code is under `azq/`.

Stage 1 therefore targets:

* `azq/cli.py`
* `azq/finis/goals.py`
* `azq/finis/goal_manager.py`
* `azq/finis/fine.py`
* `azq/finis/storage.py` (new)
* `data/finis/goals/` (new)
* `data/finis/goals.json` (legacy read-only migration input)

This checklist exists to shorten the path from doctrine to code. It should be practical enough to use while actually committing work.

---

## Stage 1 Outcome

Stage 1 is complete when all active Finis flows read and write canonical **goal files** rather than `data/finis/goals.json`.

At the end of Stage 1:

* each goal lives in its own file under `data/finis/goals/`
* goal IDs remain stable across migration
* `goals.json` is legacy input only
* all current Finis commands use one shared storage layer
* Formam can depend on goal files without transitional glue

That is the **Stable Purpose Layer** described in the implementation plan. fileciteturn13file12turn13file13

---

## Current Stage 1 Gaps

The current implementation has these concrete mismatches with the Stage 1 objective:

* goals are stored only in `data/finis/goals.json`
* goal persistence logic is duplicated in `azq/finis/goals.py` and `azq/finis/goal_manager.py`
* `azq/finis/fine.py` also depends on the JSON helper path directly
* the live goal schema uses `goal` instead of normalized `title` and has inconsistent `created` coverage
* no file-based goal records exist in `data/finis/goals/`
* no migration boundary exists between legacy JSON input and the new filesystem source of truth fileciteturn13file9turn13file13

---

## Canonical Stage 1 Goal Schema

Every normalized goal record must expose these fields:

* `goal_id`
* `title`
* `status`
* `created`
* `description`
* `derived_from`

Stage 1 rule:

* legacy `goal` becomes canonical `title`
* missing legacy fields are filled conservatively
* noisy historical values are preserved rather than “cleaned” during migration

This keeps migration additive and honest. fileciteturn13file13turn13file14

---

## Atomic Commit Checklist

### 1. Add Stage 1 storage contract notes

**Files:**

* `AZQ_BUILD_TASKS_STAGE_1.md`

**Work:**

* record the normalized Stage 1 goal schema
* record the canonical Stage 1 storage locations:

  * `data/finis/goals/`
  * `data/finis/goals.json` as legacy migration input only
* state clearly that the live code is under `azq/`, not `src/azq/`

**Definition of done:**

* the Stage 1 implementation target is explicit and repo-local

---

### 2. Create file-based Finis storage scaffolding

**Files:**

* `azq/finis/storage.py` (new)

**Work:**

* define path constants for:

  * `data/finis/goals/`
  * `data/finis/goals.json`
* add helpers to:

  * ensure the goals directory exists
  * list goal files in stable order
  * map a `goal_id` to `data/finis/goals/FINIS_###.md`

**Definition of done:**

* one module owns all path decisions for Finis goal persistence

---

### 3. Define the canonical goal record model

**Files:**

* `azq/finis/storage.py`

**Work:**

* add normalization helpers that convert legacy JSON-shaped goal records into the Stage 1 schema
* map legacy `goal` to canonical `title`
* ensure every normalized record contains:

  * `goal_id`
  * `title`
  * `status`
  * `created`
  * `description`
  * `derived_from`
* decide and document fallback behavior for missing legacy fields:

  * missing `created`
  * missing `description`
  * missing `derived_from`

**Definition of done:**

* one function can take old JSON-shaped data and return a complete Stage 1 goal record

---

### 4. Implement goal file read/write format

**Files:**

* `azq/finis/storage.py`

**Work:**

* choose a diff-friendly on-disk format for `FINIS_###.md`
* implement serializer and parser helpers
* ensure each goal file is human-readable and preserves normalized fields clearly
* keep the format simple enough for future Formam code to read without transitional glue

**Definition of done:**

* a normalized goal can be written to and read from a single Markdown file without loss of required Stage 1 fields

---

### 5. Implement repository-level goal reads from file storage

**Files:**

* `azq/finis/storage.py`

**Work:**

* add functions to:

  * load all goals from `data/finis/goals/`
  * load one goal by exact `goal_id`
  * compute the next stable `FINIS_###` id from existing file-based goals
* ensure sort order is deterministic
* ensure lookup is exact-match only on `goal_id`

**Definition of done:**

* file storage alone can support goal listing, lookup, and id allocation

---

### 6. Add legacy JSON migration reader

**Files:**

* `azq/finis/storage.py`

**Work:**

* add a dedicated legacy reader for `data/finis/goals.json`
* make it read-only by design
* keep legacy parsing separate from canonical file-based reads
* handle absent legacy JSON cleanly
* handle malformed legacy JSON defensively enough that migration failures are diagnosable

**Definition of done:**

* the codebase can read old JSON state without treating it as the canonical write target

---

### 7. Implement one-way migration into goal files

**Files:**

* `azq/finis/storage.py`
* `data/finis/goals/`

**Work:**

* add migration logic that:

  * reads `data/finis/goals.json`
  * normalizes each record
  * writes `data/finis/goals/FINIS_###.md`
* preserve existing `goal_id` values exactly
* do not generate new ids for already-known legacy goals
* make migration idempotent enough to avoid duplicating already-migrated files

**Definition of done:**

* a legacy JSON repository can be converted into file-based goal records without changing ids

---

### 8. Choose and wire the migration trigger

**Files:**

* `azq/finis/storage.py`
* possibly `azq/cli.py`

**Work:**

* implement either:

  * automatic migration on first load, or
  * a one-time migration command
* prefer the smallest approach that keeps Stage 1 usable immediately
* if using automatic migration, ensure it runs before any command writes new goal state
* if using a command, ensure the rest of Stage 1 cannot silently continue writing only to JSON

**Recommendation:**

* use automatic migration on first Finis read/write, but make it loud and inspectable

**Definition of done:**

* there is one clear, deterministic path from legacy JSON state to file-backed state

---

### 9. Refactor `azq goals` onto the shared storage layer

**Files:**

* `azq/finis/goals.py`

**Work:**

* stop owning JSON persistence helpers inside `goals.py`
* replace direct JSON reads with storage-layer reads
* update display code to read `title` rather than legacy `goal`
* keep the command behavior focused on active goals unless intentionally expanded later

**Definition of done:**

* `azq goals` works from file-backed storage through `azq/finis/storage.py`

---

### 10. Refactor `azq goal add` onto the shared storage layer

**Files:**

* `azq/finis/goal_manager.py`

**Work:**

* update `add_goal()` so it uses storage-layer id generation
* write new goals only to `data/finis/goals/FINIS_###.md`
* populate the normalized schema for newly created records
* stop writing new state to `data/finis/goals.json`

**Definition of done:**

* manual goal creation produces a canonical goal file and leaves legacy JSON untouched

---

### 11. Refactor `azq goal close` and `azq goal archive` onto the shared storage layer

**Files:**

* `azq/finis/goal_manager.py`

**Work:**

* update `close_goal()` and `archive_goal()` to load by exact `goal_id`
* persist status changes by rewriting the canonical goal file
* stop using in-memory list mutation tied to JSON saves

**Definition of done:**

* goal state transitions operate on individual file-backed goal records

---

### 12. Refactor `azq fine` onto the shared storage layer

**Files:**

* `azq/finis/fine.py`

**Work:**

* read existing goals through `azq/finis/storage.py`
* update candidate dedupe logic to compare against canonical `title`
* ensure newly accepted goals are written as normalized goal files
* ensure `derived_from` continues to capture spark backlinks
* remove remaining writes to `data/finis/goals.json`

**Definition of done:**

* the Finis intake flow and the manual goal commands use the same repository logic

---

### 13. Remove duplicated JSON persistence helpers from Finis modules

**Files:**

* `azq/finis/goals.py`
* `azq/finis/goal_manager.py`
* `azq/finis/fine.py`

**Work:**

* delete redundant `load_goals`, `save_goals`, and `next_goal_id` implementations
* replace imports that still point at transitional helpers
* route all goal persistence flows through one storage module

**Definition of done:**

* all goal persistence flows route through one storage module

---

### 14. Create initial goal-file fixtures on disk

**Files:**

* `data/finis/goals/`

**Work:**

* create `data/finis/goals/`
* add migrated `FINIS_###.md` files for the current repository state if committed sample data is desired
* leave `data/finis/goals.json` present only as legacy input until migration stability is confirmed

**Definition of done:**

* the repository visibly teaches the file-based Finis model on disk

---

### 15. Add regression tests for Stage 1 storage behavior

**Files:**

* `tests/` or `tests/fixtures/`

**Work:**

* add tests for:

  * legacy JSON normalization
  * goal file round-trip read/write
  * next id generation from file-backed goals
  * migration idempotence
  * `goal add` writing only goal files
  * `goal close` and `goal archive` updating file-backed state
  * `fine` writing canonical records with `derived_from`
* keep tests focused on storage invariants and CLI-visible behavior

**Definition of done:**

* Stage 1 behavior is locked by tests rather than manual inspection alone

---

### 16. Update repo docs that Stage 1 changes will invalidate

**Files:**

* `AZQ_BOOTSTRAP.md`
* `README.md`
* any Finis-specific notes

**Work:**

* update docs that still present `data/finis/goals.json` as the active source of truth
* clarify that file-backed goals are canonical and JSON is migration-only legacy input
* align terminology around `title` vs `goal`

**Definition of done:**

* the docs no longer teach the pre-Stage-1 storage model

---

## Commit Grouping Suggestion

If you want these as sensible commit waves rather than 16 single-file nibbles, use this grouping:

### Wave A — Storage foundation

* tasks 2–6

### Wave B — Migration

* tasks 7–8

### Wave C — Command refactor

* tasks 9–13

### Wave D — Evidence and safety net

* tasks 14–16

This keeps each wave reviewable while still respecting atomicity.

---

## Stage 1 Exit Audit

Stage 1 is done when all of the following are true:

* each goal is stored as one `FINIS_###.md` file
* `azq goals` reads from file-backed storage
* `azq goal add` writes only file-backed storage
* `azq goal close` writes only file-backed storage
* `azq goal archive` writes only file-backed storage
* `azq fine` writes only file-backed storage
* `data/finis/goals.json` is never used as an active write target
* goal ids remain stable across migration
* goal records expose `goal_id`, `title`, `status`, `created`, `description`, and `derived_from`
* the resulting files are readable and diff-friendly
* later engines can resolve goals from filesystem records without transitional JSON helpers

---

## Closing

Stage 1 is not glamorous.
It is foundation work.

But this is the layer that lets Formam stand on stone instead of swamp.

Do this carefully once, and every later engine gets simpler.

