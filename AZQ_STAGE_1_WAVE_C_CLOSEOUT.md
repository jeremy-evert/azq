# AZQ Stage 1 Wave C Closeout

## Metadata

* **Stage:** Stage 1 - Normalize Finis Storage
* **Wave:** C
* **Classification:** Closeout
* **Intent:** move Stage 1 from functional implementation to stable baseline
* **Scope rule:** no further Stage 1 expansion beyond verification, documentation alignment, and runner resilience
* **Next boundary:** Formam work begins only after this closeout wave is complete

---

## Purpose

Wave C is the final closeout wave for Stage 1.

Wave A established the storage foundation.
Wave B moved the active Finis command path onto canonical file-backed goal records.
Wave C now hardens that work so Stage 1 exits with a stable baseline rather than a merely functional implementation.

This wave is intentionally narrow.
It exists to:

* add a regression safety net around the new canonical storage model
* align the docs with the file-backed truth
* make the Codex runner exit cleanly when the wave is complete

Wave C should **not** broaden into new engine work, new Finis features, or pre-Formam architecture.

---

## Closeout Exit Target

Wave C is complete when all of the following are true:

* regression tests cover the highest-risk Stage 1 storage and command paths
* `AZQ_BOOTSTRAP.md` and `README.md` teach the canonical file-backed goal model
* `data/finis/goals.json` is described only as legacy migration input, never as active truth
* the wave runner exits gracefully with a report when no tasks remain
* Stage 1 can be declared complete without reopening scope

---

## Work Packages

### [ ] Package 1 - Regression Test Suite

**Goal**

Protect the canonical Stage 1 baseline with automated coverage over migration, storage normalization, and the main Finis command path.

**Tasks**

* [ ] add automated tests for legacy JSON normalization into the canonical goal schema
* [ ] add automated tests for goal file round-trip behavior so canonical goal records can be written and read without loss
* [ ] add automated tests for next-id generation from existing `FINIS_###.md` goal files
* [ ] add automated tests for migration idempotence so repeated migration does not duplicate or corrupt canonical goal files
* [ ] validate the core command flows for `azq goal add`, `azq goal close`, and `azq goal archive`
* [ ] verify canonical record writing, including correct `derived_from` handling

**Definition of done**

* [ ] the highest-risk Stage 1 storage and command flows are covered by automated regression tests
* [ ] the tests prove the canonical file-backed goal model behaves deterministically

---

### [ ] Package 2 - Documentation Alignment

**Goal**

Make the operator-facing docs tell the same truth as the live Stage 1 system.

**Tasks**

* [ ] refactor `AZQ_BOOTSTRAP.md` so bootstrap instructions no longer present `data/finis/goals.json` as the active write target
* [ ] refactor `README.md` so the project overview reflects the canonical file-backed goal model
* [ ] remove all references that describe `data/finis/goals.json` as the active system of record
* [ ] explicitly define the file-backed goal model under `data/finis/goals/` as the canonical system of record
* [ ] keep the documentation language aligned with the existing Stage 1 vocabulary and closeout intent

**Definition of done**

* [ ] the docs no longer teach the pre-Stage-1 Finis storage model
* [ ] a new operator can read the docs and understand that canonical goals live as one file per goal

---

### [ ] Package 3 - Runner Resilience (CLI Polish)

**Goal**

Make the wave runner behave like a closeout tool rather than a brittle loop when all assigned work is finished.

**Tasks**

* [ ] modify `run_wave_b_step.sh` or the generic runner path so completion is treated as a successful terminal state
* [ ] add a graceful-exit branch for the no-tasks-remaining case
* [ ] make the runner emit a summary report when no tasks remain
* [ ] make the runner print an explicit `Stage 1 Complete` status message instead of returning a non-zero exit code
* [ ] keep the change narrow and compatible with the current Stage 1 runner flow

**Definition of done**

* [ ] the runner exits successfully when the wave backlog is exhausted
* [ ] the operator receives a final report and clear Stage 1 completion signal

---

## Closeout Rule

All tasks in this manifest start as incomplete by design.
This file is the final Stage 1 closeout wave and should be used to prevent further scope creep before Formam implementation begins.
