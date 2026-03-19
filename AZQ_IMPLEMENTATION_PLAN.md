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
````

The build order is intentionally strict, but it now reflects the actual planning loop AZQ is meant to support:

1. preserve the canonical Finis, Formam, and Agenda baselines
2. deepen Finis so it can shape sparks into better goals with LLM assistance
3. deepen Formam so it can shape goals into useful deliverables and maps with LLM assistance
4. deepen Agenda so it can shape deliverables into commit-sized tasks, dedupe them, build dependency graphs, and prepare Codex execution
5. implement Domum
6. add doctor/status
7. remove destructive delete paths

That order keeps doctrine and practice aligned.

AZQ is not meant to be only a filesystem ledger.
It is meant to be a craft system where the existing engines do real shaping work:

* **Finis** should help define goals
* **Formam** should help define deliverables and maps
* **Agenda** should help define tasks and execution structure
* **Domum** should steward what has been built

There is no new public craft layer in this plan.
If internal helper code is borrowed from other projects or scripts, it should be absorbed into the existing engine structure rather than exposed as a sixth public engine.

---

## Planning Principles

All implementation work should obey the following rules:

* preserve durable evidence at every stage
* prefer additive migration over destructive conversion
* introduce archive paths before removing anything permanently
* keep each engine small and filesystem-driven
* add read commands before aggressive write automation when a stage is new
* do not allow later-stage objects without a traceable parent
* keep the CLI aligned with the craft stages and filesystem pipeline
* treat LLM output as a proposal artifact until it is accepted into canonical craft storage
* keep confidence checks, retries, and escalation explicit rather than magical
* keep one canonical planning path rather than multiple overlapping helper scripts
* make Codex-facing task sets deterministic, inspectable, and diff-friendly
* prefer one visible source of truth over hidden in-memory orchestration

These principles are not decoration.
They are the guardrails that keep the implementation aligned with the charter and state model.

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
* `azq goal archive <id>`

This means AZQ can currently complete the first three live craft layers:

```text
capture -> spark -> goal -> deliverable -> map -> task -> dag
```

That is enough to reach an actionable Stage 3 baseline, but not enough for the intended five-engine architecture or for the actual LLM-assisted planning workflow Jeremy uses in other places.

### Structural mismatches to resolve

The main mismatches between doctrine and implementation are:

* `finis` currently stores and lists goals, but it does not yet deeply shape sparks into refined goals with questioning, narrowing, or tractability judgment
* `formam` currently builds stub deliverables and maps, but it does not yet expand, prioritize, or refine deliverables with LLM help
* `agenda` currently builds stub tasks and goal-level DAGs, but it does not yet decompose deliverables into commit-sized tasks, dedupe them, or prepare them cleanly for Codex
* planning scripts that already perform expansion, decomposition, DAG generation, and dedupe exist outside the AZQ engine structure
* the implementation plan must absorb that existing functionality into the proper craft engines instead of waiting for archive and health stages to somehow produce it
* `azq spark rm` still teaches destructive deletion in a system whose state model explicitly prefers archive over prune and rejects silent loss
* there is no archive layer yet protecting prior artifacts
* there is no repository-wide health or maturity reader even though the state model defines both

---

## Stage 1: Normalize Finis Storage

### Objective

Move `finis` from transitional JSON storage to first-class goal files so the on-disk structure matches the filesystem and state models.

### Why first

Finis is already live, but its storage model contradicts the architectural documents. Later engines need stable goal records, stable IDs, explicit status fields, and traceable backlinks. Without that, Formam sits on mud.

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

The craft doctrine is explicit: form comes before execution. If AZQ creates tasks before deliverables, it collapses into undisciplined activity tracking.

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
* Formam should define boundaries of work, not task lists

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
* the repository can truthfully reach `formed` from visible files

---

## Stage 3: Implement Agenda

### Objective

Turn deliverables into executable tasks with visible work logs and dependency order, and treat that file-backed Agenda layer as the current live Stage 3 baseline.

### Why third

Agenda is only useful once Formam has defined what should exist. Tasks must serve deliverables rather than replace them.

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
* blocked work must become a first-class visible state, not a vague feeling

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
* the trace chain `task -> deliverable -> goal` is machine-checkable and human-readable

---

## Stage 4: Deepen Finis Into An LLM-Assisted Goal-Shaping Layer

### Objective

Extend Finis so it does real goal-shaping work rather than only storing accepted goals.

Finis should be the stage that takes sparks, weighs them, tests their spirit, asks narrowing questions, judges likely usefulness and attainability, and helps the user turn early sparks into better goals.

### Why fourth

This is the first missing layer in the actual working loop.
The repository already captures sparks and stores goals, but it does not yet provide the assisted shaping behavior that the craft model implies Finis should own.

### Scope

* deepen `azq fine` from simple candidate promotion into guided goal shaping
* allow Finis to inspect one or more spark bundles and propose:

  * candidate goals
  * goal summaries
  * tractability notes
  * usefulness notes
  * suggested narrowing questions
  * optional manifesto or intent drafts tied to a goal
* keep the accepted canonical goal record under `data/finis/goals/`
* add proposal artifacts under Finis rather than inventing a new public craft engine

### Recommended internal file work

* add `azq/finis/analysis.py`
* add `azq/finis/questions.py`
* add `azq/finis/llm.py`
* add `azq/finis/proposals.py`
* extend `azq/finis/cli.py` and `azq/finis/router.py`
* create proposal homes such as:

  * `data/finis/proposals/`
  * `data/finis/notes/`

These proposal paths are implementation details of Finis, not a new public craft layer.

### Design constraints

* Finis should not silently overwrite accepted goals with LLM output
* proposals should remain inspectable and diff-friendly
* the user should be able to reject, revise, or accept a proposed goal
* narrowing questions should be visible rather than hidden in a monolithic chat transcript
* usefulness and attainability should be framed as judgment aids, not false certainty
* any manifesto or intent draft remains a Finis artifact attached to the goal context rather than a new standalone engine

### Recommended first commands

The exact names may vary, but the live command surface should eventually support behavior equivalent to:

* `azq fine`
* `azq fine inspect <spark_id>`
* `azq fine shape <spark_id>`
* `azq fine questions <spark_id or goal_id>`

The important thing is that the public craft story stays the same: Finis shapes goals.

### Exit criteria

* Finis can read sparks and propose better goals with visible reasoning
* Finis can ask narrowing questions before the user accepts a goal
* accepted goals remain canonical Markdown goal records
* proposal and note artifacts live inside Finis rather than in ad hoc helper folders
* the move from spark to goal becomes materially more useful than simple storage

---

## Stage 5: Deepen Formam Into An LLM-Assisted Deliverable-Shaping Layer

### Objective

Extend Formam so it can take a goal and help shape it into useful deliverables, expanded deliverables, and maps that distinguish what must be built now from what can wait.

### Why fifth

Once Finis can shape better goals, Formam becomes the natural place to shape those goals into artifact boundaries and structured plans.
This is where the existing deliverable-expansion scripts belong conceptually.

### Scope

* deepen `azq form build <goal_id>` from stub generation into assisted deliverable shaping
* add deliverable expansion, prioritization, and map refinement
* absorb the existing deliverable-expansion logic into Formam internals
* allow Formam to generate:

  * proposed deliverables
  * expanded deliverable descriptions
  * priority ordering
  * first-now versus later distinctions
  * map refinements and dependency notes
* keep canonical accepted deliverables and maps under `data/form/`

### Recommended internal file work

* add `azq/formam/expand.py`
* add `azq/formam/prioritize.py`
* add `azq/formam/llm.py`
* add `azq/formam/proposals.py`
* extend `azq/formam/build.py`, `azq/formam/maps.py`, and router/CLI wiring
* create proposal homes such as:

  * `data/form/proposals/`
  * `data/form/expansions/`

These are Formam internals, not a new public engine.

### Design constraints

* Formam should define artifact boundaries, not jump directly to task lists
* expanded deliverables should remain inspectable proposal artifacts until accepted
* map generation should stay visible and file-backed
* Formam should help narrow scope, not endlessly widen it
* prioritization should support “build now” versus “wait until later”
* deliverable generation should preserve traceability back to the parent goal

### Recommended first commands

The exact names may vary, but the public behavior should remain inside Formam and support capabilities equivalent to:

* `azq form build <goal_id>`
* `azq form expand <goal_id or deliverable_id>`
* `azq form prioritize <goal_id>`
* `azq form map <goal_id>`

### Exit criteria

* Formam can produce more useful deliverables than a single stub file
* deliverable expansions and prioritization are visible on disk
* accepted deliverables remain canonical records under `data/form/deliverables/`
* goal maps become meaningful planning artifacts rather than placeholders
* the move from goal to deliverable becomes materially more useful than simple stub generation

---

## Stage 6: Deepen Agenda Into An LLM-Assisted Task-And-Codex Layer

### Objective

Extend Agenda so it can take deliverables and shape them into commit-sized tasks, dedupe them, build dependency graphs, and prepare them for Codex execution.

This is where the existing task decomposition, dedupe, DAG, and Codex-preparation scripts belong conceptually.

### Why sixth

Agenda is the natural home for executable work.
The current Stage 3 baseline proves the file-backed task system.
The next step is to make Agenda smart enough to generate and prepare the right work rather than only store one stub task.

### Scope

* deepen `azq agenda build <deliverable_id>` from stub-task generation into assisted task shaping
* absorb task decomposition logic, DAG building logic, and dedupe logic into Agenda internals
* add Codex preparation and reporting as Agenda-owned execution support
* allow Agenda to generate:

  * commit-sized task proposals
  * dependency graphs
  * execution levels
  * deduped task sets
  * Codex-ready task subsets
  * execution reports

### Recommended internal file work

* add `azq/agenda/decompose.py`
* add `azq/agenda/dedupe.py`
* add `azq/agenda/dag_builder.py`
* add `azq/agenda/codex.py`
* add `azq/agenda/llm.py`
* add `azq/agenda/proposals.py`
* extend `azq/agenda/build.py`, `azq/agenda/dags.py`, and router/CLI wiring
* create proposal and execution homes such as:

  * `data/agenda/proposals/`
  * `data/agenda/reports/`
  * `data/agenda/runs/`

These remain Agenda internals, not a new public engine.

### Design constraints

* Agenda should decompose one deliverable at a time into tasks that fit into roughly half an hour and one commit message
* generated tasks should remain proposal artifacts until accepted into canonical `data/agenda/tasks/`
* dedupe should be explicit and reversible
* DAG generation should remain deterministic from task inputs and outputs
* Codex preparation should not destroy the full task set
* execution reports should remain durable and inspectable on disk
* Agenda should own the bridge from deliverable to executable work rather than relying on scattered side scripts

### Recommended first commands

The exact names may vary, but the public behavior should stay under Agenda and support capabilities equivalent to:

* `azq agenda build <deliverable_id>`
* `azq agenda expand <deliverable_id>`
* `azq agenda dedupe <deliverable_id>`
* `azq agenda dag <deliverable_id>`
* `azq agenda codex prepare <deliverable_id>`
* `azq agenda codex run <deliverable_id>`
* `azq agenda codex report <deliverable_id>`

The important point is that task shaping and Codex preparation remain inside Agenda as part of the public craft flow.

### Exit criteria

* Agenda can produce commit-sized task proposals from a deliverable
* Agenda can dedupe task proposals and build deterministic DAG artifacts
* accepted tasks remain canonical records under `data/agenda/tasks/`
* Codex execution can be prepared from Agenda-owned artifacts without manual copy-paste glue
* the move from deliverable to executable work becomes materially more useful than single-task stub writing

---

## Stage 7: Implement Domum

### Objective

Add stewardship: archive, prune, and review operations that keep AZQ trustworthy as it accumulates craft artifacts.

### Why seventh

Before adding more mutating behavior, the system needs a safe place for finished and stale material to go. Domum protects inspectability and prevents silent loss.

### Scope

* add `azq/domum/`
* create `data/archive/`
* create archive subdirectories aligned to the state model:

  * `data/archive/sparks/`
  * `data/archive/goals/`
  * `data/archive/deliverables/`
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
* archive failure must be non-destructive: active artifacts remain in place if the move is incomplete
* Domum should steward accepted craft records and accepted supporting artifacts, not confuse proposals with canonical active records

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

## Stage 8: Add Doctor and Status

### Objective

Add repository-wide read commands that report maturity and health without mutating state.

### Why eighth

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
* contradictions between visible files and expected state rules

### Exit criteria

* `azq status` reads the repository without side effects
* `azq doctor` reports concrete issues tied to files
* maturity and health are derived from on-disk evidence, not hidden state
* the repository can explain itself without hand-waving

---

## Stage 9: Remove Destructive Delete Paths

### Objective

Eliminate silent permanent deletion from the live system.

### Why last

Permanent deletion should only be removed after archive and health mechanisms exist. Otherwise the system loses a capability before a safer replacement is in place.

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
* add fixtures under `tests/fixtures/` for migration, planning, and health checks
* document file formats as they stabilize
* make backlinks mandatory wherever the state model requires them
* keep one canonical public API per subsystem
* keep confidence checks, retries, and escalation behavior inspectable
* ensure proposal artifacts clearly distinguish proposal state from accepted canonical state
* absorb external helper scripts into existing engine homes instead of preserving overlapping parallel workflows indefinitely

### Priority test coverage

Start with tests for:

* Finis migration from `goals.json` to goal files
* parent-child integrity across `goal -> deliverable -> task`
* Finis proposal shaping and narrowing-question behavior
* Formam deliverable expansion and prioritization behavior
* Agenda decomposition determinism, dedupe determinism, and DAG determinism
* archive non-destructiveness
* `doctor` detection of orphaned and malformed artifacts
* command runs that fail after partial work and must preserve durable evidence

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

### Milestone 4: Intelligent Goal Shaping

Deliver:

* Finis LLM-assisted goal shaping
* narrowing questions
* tractability and usefulness notes
* proposal artifacts attached to Finis

Result:

* AZQ can move from spark to better goals rather than only storing accepted titles

### Milestone 5: Intelligent Deliverable Shaping

Deliver:

* Formam deliverable expansion
* prioritization
* useful map refinement

Result:

* AZQ can move from goals to useful deliverables rather than only writing stubs

### Milestone 6: Intelligent Task And Codex Preparation

Deliver:

* Agenda task decomposition
* task dedupe
* deterministic DAG generation
* Codex preparation and reporting

Result:

* AZQ can move from deliverables to executable work without relying on side scripts

### Milestone 7: Stewardship Layer

Deliver:

* Domum module
* archive paths
* review flow

Result:

* AZQ can preserve history instead of deleting it

### Milestone 8: Repository Introspection

Deliver:

* `azq status`
* `azq doctor`
* health and maturity classification

Result:

* AZQ can explain its own condition from disk

### Milestone 9: Delete-Free Craft Loop

Deliver:

* removal of destructive delete paths
* archive-first semantics across the CLI

Result:

* doctrine and implementation are aligned

---

## Definition of Done

AZQ reaches the intended five-engine baseline when all of the following are true:

* each engine has a code module and a working CLI surface
* Finis, Formam, and Agenda do real shaping work with visible LLM-assisted proposal artifacts
* each craft stage writes durable artifacts to its own filesystem home
* every later-stage object has a traceable earlier-stage parent
* archive exists before destructive removal disappears
* `status` and `doctor` can classify the repository from visible evidence
* the practical command flow matches the doctrinal pipeline
* the repository can move from `empty` to `kept` without violating the state model

At that point, AZQ is no longer only a partial capture-and-goals prototype.
It is a coherent five-engine craft system where the engines mean what their names imply.

---

## Closing

This plan is not a wishlist.
It is the build order that keeps AZQ honest.

Implement the stages in order.
Do not skip form.
Do not let tasks outrun structure.
Do not add deletion before stewardship.
Do not add a new public engine when the existing craft layers should own the work.
Do not leave the best planning behavior trapped in side scripts when it belongs inside Finis, Formam, and Agenda.

If this order is respected, doctrine and code will converge.
If it is ignored, AZQ will decay into the kind of system it was designed not to become.

```

This version keeps the public story clean:

- **Finis** becomes the LLM-assisted goal-shaping layer
- **Formam** becomes the LLM-assisted deliverable-shaping layer
- **Agenda** becomes the LLM-assisted task-and-Codex layer
- **Domum** stays stewardship, archive, review, and later status/doctor support
- **Indago stays offstage** and only contributes internal implementation ideas if needed.
