# AZQ Implementation Plan

## Purpose

This document translates the AZQ doctrine into a staged engineering roadmap.

The repository already implements part of the first two engines:

* `scintilla` exists and writes durable spark artifacts
* `finis` exists, but still uses transitional JSON storage
* `formam`, `agenda`, and `domum` are specified in documents but not yet implemented in code

The goal of this plan is to move from the current partial system to a coherent five-engine system without violating the craft order:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
```

The build order is intentionally strict:

1. normalize Finis storage
2. implement Formam
3. implement Agenda
4. implement Domum
5. add doctor/status
6. remove destructive delete paths

That order connects doctrine to code and prevents AZQ from becoming a task manager before it becomes a craft system.

---

## Current Baseline

### Implemented now

* `azq capture`
* `azq sparks`
* `azq spark <id>`
* `azq spark search <text>`
* `azq spark rm <id>`
* `azq fine`
* `azq goals`
* `azq goal add`
* `azq goal close <id>`
* `azq goal archive <id>`

### Structural mismatches to resolve

* `finis` stores all goals in `data/finis/goals.json`, while the filesystem model expects `data/finis/goals/FINIS_*.md`
* goal persistence logic is duplicated across [`azq/finis/goals.py`](/data/git/azq/azq/finis/goals.py) and [`azq/finis/goal_manager.py`](/data/git/azq/azq/finis/goal_manager.py)
* CLI shape in [`azq/cli.py`](/data/git/azq/azq/cli.py) does not yet match the command model for `form`, `task`, `archive`, `status`, and `doctor`
* `azq spark rm` currently deletes files permanently through [`azq/scintilla/spark_delete.py`](/data/git/azq/azq/scintilla/spark_delete.py)
* there is no archive layer protecting prior artifacts
* there is no repository-wide health or maturity reader

---

## Delivery Principles

* Preserve durable evidence at every stage.
* Prefer additive migration over destructive conversion.
* Introduce archive paths before removing anything permanently.
* Keep each engine small and filesystem-driven.
* Add read commands before write automation when a stage is new.
* Do not allow later-stage objects without a traceable parent.

---

## Stage 1: Normalize Finis Storage

### Objective

Move `finis` from transitional JSON storage to first-class goal files so the on-disk structure matches the filesystem and state models.

### Why first

Finis is already live, but its storage model contradicts the architecture documents. That makes every later engine harder because `formam` needs stable goal records, IDs, status fields, and backlinks.

### Scope

* create `data/finis/goals/`
* store one goal per file, named `FINIS_###.md`
* introduce a single goal repository module instead of duplicated JSON helpers
* keep `goals.json` readable only as a migration source, not as the long-term source of truth
* normalize goal fields:
  * `goal_id`
  * `title`
  * `status`
  * `created`
  * `description`
  * `derived_from`
* ensure `azq goals`, `azq goal add`, `azq goal close`, `azq goal archive`, and `azq fine` all use the same storage layer

### Recommended file work

* add `azq/finis/storage.py`
* update [`azq/finis/fine.py`](/data/git/azq/azq/finis/fine.py)
* update [`azq/finis/goals.py`](/data/git/azq/azq/finis/goals.py)
* update [`azq/finis/goal_manager.py`](/data/git/azq/azq/finis/goal_manager.py)
* create `data/finis/goals/`

### Migration strategy

1. Read existing `data/finis/goals.json`.
2. Write each record into `data/finis/goals/FINIS_###.md`.
3. Preserve original values where possible, even if they are noisy.
4. Mark `goals.json` as legacy input and stop writing to it.
5. Add a one-time migration command or automatic migration on first load.

### Exit criteria

* all active CLI goal flows operate from file-based storage
* goal IDs remain stable
* no command writes new state to `data/finis/goals.json`
* goal files are inspectable and diff-friendly
* `formam` can depend on file-based goals without transitional glue

---

## Stage 2: Implement Formam

### Objective

Introduce the form-building stage that turns goals into deliverables and dependency maps.

### Why second

The doctrine is explicit: form comes before execution. If AZQ creates tasks before deliverables, it collapses into undisciplined activity tracking.

### Scope

* add `azq/formam/`
* create `data/form/deliverables/`
* create `data/form/maps/`
* implement the first Formam commands:
  * `azq form build <goal_id>`
  * `azq form list`
  * `azq form show <deliverable_id>`
* define a deliverable record format with at least:
  * `deliverable_id`
  * `goal_id`
  * `title`
  * `artifact_description`
  * `dependencies`
  * `status`
* define a map artifact per goal that records deliverable relationships

### Design constraints

* one or more deliverables may descend from a goal
* every deliverable must point back to exactly one goal initially
* maps should remain human-readable, even if later exported to JSON
* Formam should define boundaries of work, not task lists

### Recommended initial implementation

* start with Markdown deliverable files
* allow manual or assisted generation from a goal file
* make `azq form build <goal_id>` generate a stub deliverable and a goal map rather than trying to solve full planning on day one

### Exit criteria

* a goal can produce at least one deliverable file and one map file
* deliverables can be listed and inspected from the CLI
* every deliverable has a valid parent goal
* no task commands are introduced before deliverables exist

---

## Stage 3: Implement Agenda

### Objective

Turn deliverables into executable tasks with visible work logs and dependency order.

### Why third

Agenda is only useful once Formam has defined what should exist. Tasks must serve deliverables rather than replace them.

### Scope

* add `azq/agenda/`
* create `data/agenda/tasks/`
* create `data/agenda/dags/`
* create `data/agenda/logs/`
* implement the first Agenda commands:
  * `azq task list`
  * `azq task start <task_id>`
  * `azq task complete <task_id>`
  * `azq agenda <deliverable_id>` or equivalent task-generation entrypoint
* define a task record format with at least:
  * `task_id`
  * `deliverable_id`
  * `description`
  * `dependencies`
  * `status`
  * `execution_notes`

### Design constraints

* every task must descend from a deliverable
* task dependencies must be inspectable on disk
* in-progress work should leave a log artifact in `data/agenda/logs/`
* task completion should not imply artifact publication automatically

### Recommended initial implementation

* keep DAGs simple JSON files
* use Markdown task records for readability
* write a work log entry when a task starts or completes
* defer advanced scheduling and prioritization until the basic trace chain is solid

### Exit criteria

* a deliverable can produce executable task files
* task start and complete transitions write durable logs
* no task exists without a valid deliverable parent
* repository state can reach `actionable` from real artifacts

---

## Stage 4: Implement Domum

### Objective

Add stewardship: archive, prune, and review operations that keep AZQ trustworthy as it accumulates artifacts.

### Why fourth

Before adding more mutating behavior, the system needs a safe place for finished and stale material to go. Domum protects inspectability and prevents silent loss.

### Scope

* add `azq/domum/`
* create `data/archive/`
* create archive subdirectories aligned to the state model:
  * `data/archive/sparks/`
  * `data/archive/goals/`
  * `data/archive/tasks/`
  * `data/archive/artifacts/`
* create `data/reports/` if review output becomes first-class
* implement the first Domum commands:
  * `azq archive ...`
  * `azq prune`
  * `azq review`

### Design constraints

* archive should move or copy durable artifacts without losing provenance
* archive actions should write a reason or manifest
* prune should be policy-based, not silent deletion
* review should summarize recent state transitions from visible files

### Recommended initial implementation

* start with goal and spark archiving
* preserve original IDs and timestamps
* write a small archive manifest next to archived objects or in a shared log
* treat failed archive as non-destructive: active artifacts remain in place if the move is incomplete

### Exit criteria

* archived material is recoverable and inspectable
* `goal archive` and future archive operations route through Domum
* review output can summarize recent work from filesystem evidence
* the repository can reach `kept` through explicit stewardship artifacts

---

## Stage 5: Add Doctor and Status

### Objective

Add repository-wide read commands that report maturity and health without mutating state.

### Why after Domum

`status` and `doctor` should describe the actual system, not a hypothetical one. They are more useful after the major object layers and archive paths exist.

### Scope

* implement `azq status`
* implement `azq doctor`
* compute repository maturity:
  * `empty`
  * `seeded`
  * `purposed`
  * `formed`
  * `actionable`
  * `realized`
  * `kept`
* compute repository health:
  * `healthy`
  * `warning`
  * `degraded`
  * `inconsistent`

### What `status` should report first

* spark count
* active goal count
* deliverable count
* open task count
* artifact count
* archive count
* maturity classification

### What `doctor` should validate first

* required directory presence
* readable artifact files
* orphaned goal, deliverable, and task chains
* malformed IDs
* missing parent references
* legacy storage still in use

### Exit criteria

* `azq status` reads the repository without side effects
* `azq doctor` reports concrete issues tied to files
* maturity and health are derived from on-disk evidence, not hidden state

---

## Stage 6: Remove Destructive Delete Paths

### Objective

Eliminate silent permanent deletion from the live system.

### Why last

Permanent deletion should only be removed after archive and health mechanisms exist. Otherwise the system loses a capability before a safer replacement is in place.

### Scope

* remove or deprecate `azq spark rm <id>`
* replace direct unlink behavior in [`azq/scintilla/spark_delete.py`](/data/git/azq/azq/scintilla/spark_delete.py) with archive-oriented behavior
* audit other destructive transitions added during implementation
* align CLI language with stewardship:
  * prefer `archive`
  * avoid `rm`
  * keep destructive actions explicit and rare

### Recommended migration path

1. Change `spark rm` into a deprecation shim that archives the spark.
2. Add `azq archive spark <id>` as the canonical command.
3. Update help text in [`azq/cli.py`](/data/git/azq/azq/cli.py).
4. Remove permanent delete behavior after the archive path is stable.

### Exit criteria

* no routine user command permanently deletes primary craft artifacts
* archival replacement exists for current delete flows
* the CLI no longer teaches users to destroy evidence

---

## Cross-Cutting Work

These tasks should be done alongside the stages above rather than treated as a separate engine:

* add tests for each state transition
* normalize ID parsing and validation across engines
* keep CLI help synchronized with the command model
* add small fixtures under `data/` or `tests/fixtures/` for migration and health checks
* document file formats as they stabilize

Priority test coverage should include:

* Finis migration from `goals.json` to goal files
* parent-child integrity across goal -> deliverable -> task
* archive non-destructiveness
* `doctor` detection of orphaned and malformed artifacts

---

## Suggested Milestones

### Milestone 1: Stable Purpose Layer

Deliver:

* normalized Finis storage
* unified goal repository code
* migration off `goals.json`

Result:

* AZQ is reliably `purposed`

### Milestone 2: Real Form Layer

Deliver:

* Formam module
* deliverable files
* map files

Result:

* AZQ can become `formed` without inventing tasks prematurely

### Milestone 3: Actionable Work Layer

Deliver:

* Agenda module
* task records
* DAGs
* work logs

Result:

* AZQ can become `actionable` from explicit deliverables

### Milestone 4: Stewardship Layer

Deliver:

* Domum module
* archive paths
* review flow

Result:

* AZQ can preserve history instead of deleting it

### Milestone 5: Repository Introspection

Deliver:

* `azq status`
* `azq doctor`
* health and maturity classification

Result:

* AZQ can explain its own condition from disk

### Milestone 6: Delete-Free Craft Loop

Deliver:

* removal of destructive delete paths
* archive-first semantics across the CLI

Result:

* doctrine and implementation are aligned

---

## Definition of Done

AZQ reaches the intended five-engine baseline when all of the following are true:

* each engine has a code module and a minimal working CLI surface
* each craft stage writes durable artifacts to its own filesystem home
* every later-stage object has a traceable earlier-stage parent
* archive exists before destructive removal disappears
* `status` and `doctor` can classify the repository from visible evidence
* the practical command flow matches the doctrinal pipeline

At that point, AZQ is no longer a partial capture-and-goals prototype. It is a coherent five-engine craft system.
