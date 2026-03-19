# AZQ Implementation Plan

## Purpose

This document translates AZQ doctrine into a staged engineering roadmap.

The repository already implements the first three craft layers in the current repository layout:

* `scintilla` exists and writes durable spark artifacts
* `finis` exists and now uses canonical file-backed goal storage
* `formam` exists and writes canonical deliverable and goal-map artifacts
* `agenda` exists and writes canonical task, DAG, and task-log artifacts
* `domum` remains planned rather than live

The goal of this plan is to move from the current Stage 3 baseline to a coherent five-engine system without violating the craft order:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
```

The build order is intentionally strict:

1. preserve the canonical Finis, Formam, and Agenda baselines
2. implement Domum
3. add doctor/status
4. remove destructive delete paths

That order connects doctrine to code and prevents AZQ from becoming a task manager before it becomes a craft system. fileciteturn11file5turn11file12

---

## Planning Principles

All implementation work should obey the following rules:

* preserve durable evidence at every stage
* prefer additive migration over destructive conversion
* introduce archive paths before removing anything permanently
* keep each engine small and filesystem-driven
* add read commands before aggressive write automation when a stage is new
* do not allow later-stage objects without a traceable parent
* keep the CLI aligned with the craft stages and filesystem pipeline fileciteturn10file2turn10file1turn10file4

These principles are not decoration. They are the guardrails that keep the implementation aligned with the charter and state model. fileciteturn10file2turn10file8

---

## Current Baseline

### Implemented now

The current repository already supports:

* `azq capture`
* `azq sparks`
* `azq spark <id>`
* `azq spark search <text>`
* `azq spark rm <id>`
* `azq fine`
* `azq goals`
* `azq goal add`
* `azq goal close <id>`
* `azq form build <goal_id>`
* `azq form list`
* `azq form show <deliverable_id>`
* `azq form map <goal_id>`
* `azq agenda build <deliverable_id>`
* `azq agenda list`
* `azq agenda show <task_id>`
* `azq agenda dag <deliverable_id>`
* `azq goal archive <id>` fileciteturn11file5

This means AZQ can currently complete the first three live craft layers:

```text
capture -> spark -> goal -> deliverable -> map -> task -> dag
```

That is enough to reach an actionable Stage 3 baseline, but not enough for the intended five-engine architecture. fileciteturn10file0turn10file5

### Structural mismatches to resolve

The main mismatches between doctrine and implementation are:

* some operator-facing docs still describe canonical Finis, Formam, and Agenda storage as future-only work rather than the live baseline
* the live storage layers now exist, but operator-facing docs still need to teach them accurately without falling back to older pre-implementation framing
* the CLI does not yet match the full long-range command model for archive, status, and doctor, and the live Stage 3 operator surface is `azq agenda ...` rather than the older split `task` and `dag` families fileciteturn10file1turn10file5
* `azq spark rm` still teaches destructive deletion in a system whose state model explicitly prefers archive over prune and rejects silent loss fileciteturn10file8turn11file5
* there is no archive layer yet protecting prior artifacts fileciteturn10file4turn11file5
* there is no repository-wide health or maturity reader even though the state model defines both fileciteturn10file8

---

## Stage 1: Normalize Finis Storage

### Objective

Move `finis` from transitional JSON storage to first-class goal files so the on-disk structure matches the filesystem and state models.

### Why first

Finis is already live, but its storage model contradicts the architectural documents. Later engines need stable goal records, stable IDs, explicit status fields, and traceable backlinks. Without that, Formam sits on mud. fileciteturn10file4turn10file8

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
* update the Finis command handlers to use that storage layer
* create `data/finis/goals/`
* preserve `data/finis/goals.json` as legacy input until migration is stable

### Migration strategy

1. Read existing `data/finis/goals.json`.
2. Write each record into `data/finis/goals/FINIS_###.md`.
3. Preserve original values where possible, even if they are noisy.
4. Mark `goals.json` as legacy input and stop writing new state to it.
5. Add either a one-time migration command or automatic migration on first load.

### Exit criteria

* all active CLI goal flows operate from file-based storage
* goal IDs remain stable
* no command writes new state to `data/finis/goals.json`
* goal files are inspectable and diff-friendly
* Formam can depend on file-based goals without transitional glue

---

## Stage 2: Implement Formam

### Objective

Introduce the form-building stage that turns goals into deliverables and dependency maps.

### Why second

The craft doctrine is explicit: form comes before execution. If AZQ creates tasks before deliverables, it collapses into undisciplined activity tracking. fileciteturn10file2turn10file6

### Scope

* add or extend `azq/formam/`
* create `data/form/deliverables/`
* create `data/form/maps/`
* implement the first Formam commands:

  * `azq form build <goal_id>`
  * `azq form list`
  * `azq form show <deliverable_id>`
  * `azq form map <goal_id>`
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
* Formam should define boundaries of work, not task lists fileciteturn10file3turn10file8

### Recommended initial implementation

* start with Markdown deliverable files
* allow manual or assisted generation from a goal file
* make `azq form build <goal_id>` generate a stub deliverable and a goal map rather than trying to solve full planning on day one
* make backlinks mandatory from deliverable to goal

### Exit criteria

* a goal can produce at least one deliverable file and one map file
* deliverables can be listed and inspected from the CLI
* every deliverable has a valid parent goal
* no task commands are introduced before deliverables exist
* the repository can truthfully reach `formed` from visible files fileciteturn10file8

---

## Stage 3: Implement Agenda

### Objective

Turn deliverables into executable tasks with visible work logs and dependency order, and treat that file-backed Agenda layer as the current live Stage 3 baseline.

### Why third

Agenda is only useful once Formam has defined what should exist. Tasks must serve deliverables rather than replace them. fileciteturn10file3turn11file13

### Live baseline

* `azq/agenda/`
* canonical task storage under `data/agenda/tasks/`
* canonical DAG storage under `data/agenda/dags/`
* canonical task-log storage under `data/agenda/logs/`
* the current Agenda commands:

  * `azq agenda build <deliverable_id>`
  * `azq agenda list`
  * `azq agenda show <task_id>`
  * `azq agenda dag <deliverable_id>`
* a canonical task record format with at least:

  * `task_id`
  * `deliverable_id`
  * `description`
  * `dependencies`
  * `status`
  * `execution_notes`
  * `created`
* a canonical goal-level DAG artifact under `data/agenda/dags/GOAL_<goal_id>_DAG.json`
* a canonical task-log artifact under `data/agenda/logs/<task_id>_LOG.md`

### Design constraints

* every task must descend from a deliverable
* `data/agenda/tasks/`, `data/agenda/dags/`, and `data/agenda/logs/` are the canonical Stage 3 system of record
* task dependencies must be inspectable on disk
* task-log evidence must remain inspectable on disk
* task completion should not imply artifact publication automatically
* blocked work must become a first-class visible state, not a vague feeling fileciteturn10file8

### Current command framing

The current operator surface is intentionally narrow:

* `azq agenda build <deliverable_id>` creates or refreshes canonical tasks for one deliverable
* `azq agenda list` reads canonical tasks from disk
* `azq agenda show <task_id>` inspects one canonical task from disk
* `azq agenda dag <deliverable_id>` refreshes and inspects the parent goal DAG reached from one exact deliverable

The older `azq task ...`, `azq dag ...`, `task start`, and `task complete` framing should not be described as the live Stage 3 command surface unless the code exposes those commands later.

### Exit criteria

* a deliverable can produce executable task files
* canonical DAG artifacts and task-log artifacts exist under `data/agenda/`
* no task exists without a valid deliverable parent
* repository state can reach `actionable` from real artifacts
* the trace chain `task -> deliverable -> goal` is machine-checkable and human-readable fileciteturn10file8turn11file9

---

## Stage 4: Implement Domum

### Objective

Add stewardship: archive, prune, and review operations that keep AZQ trustworthy as it accumulates artifacts.

### Why fourth

Before adding more mutating behavior, the system needs a safe place for finished and stale material to go. Domum protects inspectability and prevents silent loss. fileciteturn10file2turn11file11

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
* archive failure must be non-destructive: active artifacts remain in place if the move is incomplete fileciteturn11file4turn11file18

### Recommended initial implementation

* start with spark and goal archiving
* preserve original IDs and timestamps
* write a small archive manifest next to archived objects or in a shared log
* route existing `goal archive` behavior through Domum rather than leaving it embedded in Finis

### Exit criteria

* archived material is recoverable and inspectable
* `goal archive` and future archive operations route through Domum
* review output can summarize recent work from filesystem evidence
* the repository can reach `kept` through explicit stewardship artifacts

---

## Stage 5: Add Doctor and Status

### Objective

Add repository-wide read commands that report maturity and health without mutating state.

### Why fifth

`status` and `doctor` should describe the actual system, not a hypothetical one. They are more useful after the major object layers and archive paths exist. fileciteturn10file1turn10file8

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
* contradictions between visible files and expected state rules

### Exit criteria

* `azq status` reads the repository without side effects
* `azq doctor` reports concrete issues tied to files
* maturity and health are derived from on-disk evidence, not hidden state
* the repository can explain itself without hand-waving

---

## Stage 6: Remove Destructive Delete Paths

### Objective

Eliminate silent permanent deletion from the live system.

### Why last

Permanent deletion should only be removed after archive and health mechanisms exist. Otherwise the system loses a capability before a safer replacement is in place. fileciteturn11file1turn11file18

### Scope

* remove or deprecate `azq spark rm <id>`
* replace direct unlink behavior in spark deletion logic with archive-oriented behavior
* audit other destructive transitions added during implementation
* align CLI language with stewardship:

  * prefer `archive`
  * avoid `rm`
  * keep destructive actions explicit and rare

### Recommended migration path

1. Change `spark rm` into a deprecation shim that archives the spark.
2. Add `azq archive spark <id>` as the canonical command.
3. Update CLI help and bootstrap docs.
4. Remove permanent delete behavior after the archive path is stable.

### Exit criteria

* no routine user command permanently deletes primary craft artifacts
* archival replacement exists for current delete flows
* the CLI no longer teaches users to destroy evidence
* doctrine and implementation finally stop contradicting each other

---

## Cross-Cutting Work

These tasks should be done alongside the stages above rather than treated as a separate engine:

* add tests for each state transition
* normalize ID parsing and validation across engines
* keep CLI help synchronized with the command model
* add fixtures under `tests/fixtures/` for migration and health checks
* document file formats as they stabilize
* make backlinks mandatory wherever the state model requires them

### Priority test coverage

Start with tests for:

* Finis migration from `goals.json` to goal files
* parent-child integrity across `goal -> deliverable -> task`
* archive non-destructiveness
* `doctor` detection of orphaned and malformed artifacts
* command runs that fail after partial work and must preserve durable evidence fileciteturn11file4turn11file9

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
* the repository can move from `empty` to `kept` without violating the state model

At that point, AZQ is no longer a partial capture-and-goals prototype.
It is a coherent five-engine craft system.

---

## Closing

This plan is not a wishlist.
It is the build order that keeps AZQ honest.

Implement the stages in order.
Do not skip form.
Do not let tasks outrun structure.
Do not add deletion before stewardship.
Do not add hidden state where durable files should suffice.

If this order is respected, doctrine and code will converge.
If it is ignored, AZQ will decay into the kind of system it was designed not to become.
