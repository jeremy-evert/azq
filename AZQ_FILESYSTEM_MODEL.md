# AZQ Filesystem Model

## Purpose

This document defines the on-disk structure of AZQ.

The filesystem is not a storage afterthought.
It is the visible skeleton of the craft system.

A reader should be able to inspect the repository tree and understand:

* what is live now
* what artifacts are canonical
* what artifacts are proposal-stage only
* what later-stage homes are planned but not yet central to the current baseline
* how work moves from spark to archive

The guiding principle is simple:

> The filesystem should teach the architecture.

This document must tell the truth about two things at once:

1. the **current live baseline**
2. the **future filesystem direction** required by the implementation plan

---

## Governing Relationship To Other Documents

This document should be read alongside:

* `AZQ_CRAFT_CHARTER.md`
* `AZQ_COMMAND_MODEL.md`
* `AZQ_ENGINE_SPEC.md`
* `AZQ_IMPLEMENTATION_PLAN.md`
* `AZQ_STATE_MODEL.md`
* `AZQ_BOOTSTRAP.md`

Those documents define doctrine, commands, engine responsibilities, build order, lifecycle states, and bootstrap truth.

This document answers a narrower question:

> **Where do the artifacts live on disk, and what do those homes mean?**

---

## First Principle

The filesystem must preserve the craft sequence visibly:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
````

In current live terms, the repository already supports:

```text
spark -> goal -> deliverable -> task -> dag
```

That is the Stage 1 through Stage 3 baseline.

The later layers still matter, but they must not be mistaken for already-live central workflow.

---

## Core Filesystem Rules

### 1. Canonical artifacts and proposal artifacts are different

Accepted craft artifacts live in canonical homes.

Future LLM-assisted shaping work may produce proposal artifacts, but proposal homes must not silently replace canonical homes.

### 2. Engine-owned artifacts stay inside engine families

Future shaping behavior belongs inside the existing engines:

* Finis owns goal-shaping proposals
* Formam owns deliverable-shaping proposals
* Agenda owns task-shaping and Codex-preparation proposals

There is no separate public planning engine with its own top-level artifact tree.

### 3. The live baseline stays small

The current live baseline should remain easy to inspect:

* sparks
* goals
* deliverables
* maps
* tasks
* DAGs
* task logs

### 4. Later-stage homes should be named now, but not overstated

It is acceptable to define future homes for artifacts, archives, and reports, but the document must be clear about whether those homes are:

* **live now**
* **future direction**
* **optional support homes**

### 5. Directory names should favor clarity over cleverness

Short names are good.
Memorable names are good.
But the directory tree must still be readable to a tired human with a terminal open at midnight.

---

# Root Repository Layout

The repository root should remain conceptually simple.

```text
azq/
  README.md
  AZQ_BOOTSTRAP.md
  AZQ_COMMAND_MODEL.md
  AZQ_CRAFT_CHARTER.md
  AZQ_ENGINE_SPEC.md
  AZQ_FILESYSTEM_MODEL.md
  AZQ_IMPLEMENTATION_PLAN.md
  AZQ_MANIFESTO.md
  AZQ_PHILOSOPHY.md
  AZQ_STATE_MODEL.md
  azq/
  data/
  logs/
  scripts/
  tests/
```

## Root Directory Meanings

| Directory / File | Purpose                                                             |
| ---------------- | ------------------------------------------------------------------- |
| `azq/`           | source code for the live craft engines                              |
| `data/`          | durable craft artifacts and later proposal/archive/report artifacts |
| `logs/`          | operational logs                                                    |
| `scripts/`       | helper scripts and maintenance tooling                              |
| `tests/`         | unit and integration tests                                          |
| top-level docs   | doctrine, architecture, implementation, and operator guidance       |

The repository intentionally separates **code** from **artifacts**.

---

# Source Code Layout

All live engine implementations live under the package root:

```text
azq/
  __init__.py
  cli.py
  scintilla/
  finis/
  formam/
  agenda/
```

Later, the repository is expected to add:

```text
azq/
  domum/
```

## Source Module Meanings

| Module       | Role                                                      |
| ------------ | --------------------------------------------------------- |
| `scintilla/` | gather sparks                                             |
| `finis/`     | shape goals                                               |
| `formam/`    | shape deliverables and maps                               |
| `agenda/`    | shape executable work                                     |
| `domum/`     | steward, archive, review, and later support status/doctor |

The implementation plan explicitly says future intelligence should deepen these existing engines rather than split into a sixth public engine. Internal helpers may exist, but the public architecture stays five-engine.

---

# Data Layer Overview

The `data/` tree mirrors the craft system.

## Current live baseline

```text
data/
  scintilla/
  finis/
  form/
  agenda/
```

## Future broader lifecycle

```text
data/
  scintilla/
  finis/
  form/
  agenda/
  artifacts/
  archive/
  reports/
```

### Meaning of each top-level data home

| Directory         | Meaning                                                                                 | Live now               |
| ----------------- | --------------------------------------------------------------------------------------- | ---------------------- |
| `data/scintilla/` | spark capture artifacts                                                                 | yes                    |
| `data/finis/`     | goal artifacts and later goal-shaping proposals                                         | yes                    |
| `data/form/`      | deliverables, maps, and later deliverable-shaping proposals                             | yes                    |
| `data/agenda/`    | tasks, DAGs, logs, and later task/Codex proposal artifacts                              | yes                    |
| `data/artifacts/` | realized outputs of completed work                                                      | later-stage            |
| `data/archive/`   | archived craft artifacts and stewardship records                                        | later-stage            |
| `data/reports/`   | cross-cutting reports when review output becomes first-class outside engine-local homes | later-stage / optional |

The current bootstrap path only needs the first four top-level homes.
The others matter to the full lifecycle, but they are not required to prove the current live baseline.

---

# Scintilla Storage

Scintilla stores captured sparks and their immediate provenance.

```text
data/scintilla/
  audio/
  transcripts/
  sparks/
```

## Canonical homes

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
```

## Typical files

```text
data/scintilla/audio/YYYY-MM-DD_HHMMSS.wav
data/scintilla/transcripts/YYYY-MM-DD_HHMMSS.txt
data/scintilla/sparks/YYYY-MM-DD_HHMMSS.json
```

## Meaning

Pipeline:

```text
audio -> transcript -> spark
```

A spark bundle is healthy when its audio, transcript, and spark JSON remain traceable to the same capture event.

## Future direction

Possible later homes or behaviors may include archive-first spark retirement, but the active Scintilla tree should stay small.

No extra Scintilla planning tree is needed beyond the canonical spark artifacts unless later implementation proves it necessary.

---

# Finis Storage

Finis stores accepted goals and, later, goal-shaping proposal artifacts.

## Current canonical Finis tree

```text
data/finis/
  goals/
```

## Canonical goal home

```text
data/finis/goals/
```

## Typical canonical files

```text
data/finis/goals/FINIS_001.md
data/finis/goals/FINIS_002.md
```

## Canonical goal fields

A canonical goal record should support at least:

```text
goal_id
title
description
status
created
derived_from
```

## Legacy note

`data/finis/goals.json` may still exist as legacy migration input in some repositories, but it is not the long-term canonical goal store.

## Future Finis proposal homes

As Finis deepens into an LLM-assisted goal-shaping layer, proposal artifacts should remain inside Finis:

```text
data/finis/
  goals/
  proposals/
  notes/
```

### Meaning of future Finis support homes

| Directory               | Purpose                                                                      |
| ----------------------- | ---------------------------------------------------------------------------- |
| `data/finis/proposals/` | candidate goal proposals, shaping results, tractability and usefulness notes |
| `data/finis/notes/`     | manifesto, intent, and narrowing-question artifacts tied to goal work        |

These are **Finis-owned** support homes.
They are not a new public engine and should not be mistaken for accepted canonical goals.

## What no longer belongs here

The older `data/finis/reviews/` story is no longer the right primary model.
The revised implementation direction favors `proposals/` and `notes/` as clearer homes for future Finis shaping output.

---

# Formam Storage

Formam stores accepted deliverables and goal maps, and later deliverable-shaping proposal artifacts.

## Current canonical Formam tree

```text
data/form/
  deliverables/
  maps/
```

## Canonical homes

```text
data/form/deliverables/
data/form/maps/
```

## Typical canonical files

```text
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_FINIS_001_MAP.md
```

## Canonical deliverable fields

A canonical deliverable record should support at least:

```text
deliverable_id
goal_id
title
artifact_description
dependencies
status
```

## Meaning

* `deliverables/` stores the accepted structural artifacts that define what should exist
* `maps/` stores the visible relationship structure around a goal’s deliverables

## Future Formam proposal homes

As Formam deepens into an LLM-assisted deliverable-shaping layer, proposal artifacts should remain inside Formam:

```text
data/form/
  deliverables/
  maps/
  proposals/
  expansions/
```

### Meaning of future Formam support homes

| Directory               | Purpose                                                                                               |
| ----------------------- | ----------------------------------------------------------------------------------------------------- |
| `data/form/proposals/`  | candidate deliverable sets before acceptance                                                          |
| `data/form/expansions/` | expanded deliverable descriptions, prioritization notes, and first-now versus later shaping artifacts |

These are Formam-owned support homes.
They are not separate engines and should not silently overwrite accepted canonical deliverables.

---

# Agenda Storage

Agenda stores accepted tasks, goal-level DAGs, task logs, and later task-shaping / Codex-preparation artifacts.

## Current canonical Agenda tree

```text
data/agenda/
  tasks/
  dags/
  logs/
```

## Canonical homes

```text
data/agenda/tasks/
data/agenda/dags/
data/agenda/logs/
```

## Typical canonical files

```text
data/agenda/tasks/TASK_001.md
data/agenda/dags/GOAL_FINIS_001_DAG.json
data/agenda/logs/TASK_001_LOG.md
```

## Important canonical naming note

The current canonical DAG shape is:

```text
GOAL_<goal_id>_DAG.json
```

not older forms like:

```text
FINIS_001_dag.json
```

The DAG artifact is goal-scoped even when refreshed from an exact deliverable.

## Canonical task fields

A canonical task record should support at least:

```text
task_id
deliverable_id
description
dependencies
status
execution_notes
created
```

## Meaning

* `tasks/` stores accepted executable work items
* `dags/` stores goal-level dependency graphs derived from deliverable and task relationships
* `logs/` stores task-log evidence

## Future Agenda support homes

As Agenda deepens into an LLM-assisted task-and-Codex layer, support artifacts should remain inside Agenda:

```text
data/agenda/
  tasks/
  dags/
  logs/
  proposals/
  reports/
  runs/
```

### Meaning of future Agenda support homes

| Directory                | Purpose                                                                          |
| ------------------------ | -------------------------------------------------------------------------------- |
| `data/agenda/proposals/` | generated task proposals before acceptance                                       |
| `data/agenda/reports/`   | task shaping, dedupe, DAG, and Codex execution reports owned by Agenda           |
| `data/agenda/runs/`      | run-level metadata for task generation, Codex preparation, or execution sessions |

These are Agenda-owned support homes.
They should not become a separate public execution engine.

---

# Artifact Storage

Artifacts are realized outcomes of work.

This is a real lifecycle band in the state model even though the current live baseline does not yet emphasize it heavily.

## Future artifact tree

```text
data/artifacts/
```

This home may later grow into subdirectories such as:

```text
data/artifacts/code/
data/artifacts/docs/
data/artifacts/notes/
data/artifacts/modules/
```

Use those only when realized outputs are mature enough that keeping them grouped separately is useful.

## Important constraint

`data/artifacts/` is part of the lifecycle model, but it is **not** required for the current bootstrap baseline.
It becomes central once work is being realized and preserved as outcomes rather than only as plans.

---

# Archive Storage

Archive is Domum’s future primary territory.

Nothing important should disappear silently.
Archive preserves history while keeping active craft homes cleaner.

## Future archive tree

```text
data/archive/
  sparks/
  goals/
  deliverables/
  tasks/
  artifacts/
```

### Meaning

| Directory                    | Purpose                   |
| ---------------------------- | ------------------------- |
| `data/archive/sparks/`       | retired spark bundles     |
| `data/archive/goals/`        | archived goals            |
| `data/archive/deliverables/` | archived deliverables     |
| `data/archive/tasks/`        | archived tasks            |
| `data/archive/artifacts/`    | archived realized outputs |

Archive behavior should preserve provenance.
Archive moves or archive manifests should remain inspectable.

## What archive is not

Archive is not a trash can.
It is not a hidden graveyard.
It is the preserved memory of work that is no longer active.

---

# Reports Storage

Some reports belong inside engine-specific homes.
Some later review output may deserve a cross-cutting home.

## Cross-cutting future report home

```text
data/reports/
```

Use this only when the report is genuinely repository-wide or Domum-owned.

Examples might eventually include:

* repository review reports
* stewardship summaries
* health snapshots
* maturity summaries

If a report is really a task-shaping or Codex-preparation report, it should stay under `data/agenda/reports/` rather than being promoted to `data/reports/` too early.

---

# Logs

Operational logs live outside the craft pipeline.

```text
logs/
```

Examples may include:

```text
logs/capture.log
logs/transcription.log
logs/agenda.log
logs/maintenance.log
```

Logs are useful for diagnostics, but they are not canonical craft artifacts.

---

# Scripts

Automation helpers and maintenance tools may live here:

```text
scripts/
```

This directory is for helper tooling, maintenance utilities, or migration support.
It is not where canonical craft artifacts should live.

As engine functionality is absorbed into the real AZQ modules, this directory should become less central to the core craft flow.

---

# Tests

Tests live here:

```text
tests/
```

The repository should continue expanding coverage for:

* parent-child integrity
* proposal artifact integrity
* deterministic DAG generation
* archive non-destructiveness
* repository health detection

Tests do not belong in the artifact tree.
They validate the tree.

---

# Example Current Live Tree

The smallest truthful live tree today looks like:

```text
azq/
  azq/
    cli.py
    scintilla/
    finis/
    formam/
    agenda/
  data/
    scintilla/
      audio/
      transcripts/
      sparks/
    finis/
      goals/
    form/
      deliverables/
      maps/
    agenda/
      tasks/
      dags/
      logs/
  logs/
  scripts/
  tests/
```

That is the current Stage 3-capable filesystem baseline.

---

# Example Future Full Tree

As the implementation plan matures, the broader tree may look like:

```text
azq/
  azq/
    cli.py
    scintilla/
    finis/
    formam/
    agenda/
    domum/
  data/
    scintilla/
      audio/
      transcripts/
      sparks/
    finis/
      goals/
      proposals/
      notes/
    form/
      deliverables/
      maps/
      proposals/
      expansions/
    agenda/
      tasks/
      dags/
      logs/
      proposals/
      reports/
      runs/
    artifacts/
    archive/
      sparks/
      goals/
      deliverables/
      tasks/
      artifacts/
    reports/
  logs/
  scripts/
  tests/
```

This is a **future direction tree**, not a claim that every directory already exists or is central to current bootstrap.

---

# Initialization Guidance

When initializing a new AZQ repository for the current live baseline, these directories can be created immediately:

```text
data/scintilla/audio
data/scintilla/transcripts
data/scintilla/sparks
data/finis/goals
data/form/deliverables
data/form/maps
data/agenda/tasks
data/agenda/dags
data/agenda/logs
logs
scripts
tests
```

That is enough to support the current bootstrap path.

As later stages land, it becomes reasonable to add:

```text
data/finis/proposals
data/finis/notes
data/form/proposals
data/form/expansions
data/agenda/proposals
data/agenda/reports
data/agenda/runs
data/artifacts
data/archive
data/reports
```

Those should appear when the implementation actually reaches the stage that needs them.

---

# Design Principles

## Transparency

Intermediate artifacts remain visible and inspectable.

## Durability

The system favors plain durable files:

```text
markdown
json
csv
```

## Simplicity

The tree should remain shallow enough that a human can understand it from the terminal.

## Reversibility

Work should remain traceable backward:

```text
task -> deliverable -> goal -> spark
```

and later:

```text
archive -> original active artifact provenance
```

## Honest Growth

Future homes should be named clearly, but not overstated as already central when they are still planned.

---

# Closing

The filesystem is the visible skeleton of AZQ.

If the tree is honest, the architecture stays teachable.
If the tree lies, every later document and command becomes harder to trust.

So the filesystem model should do three things well:

1. teach the current live baseline
2. make future growth legible
3. keep proposal artifacts, canonical artifacts, and archived artifacts clearly distinct

That is how the filesystem teaches the architecture instead of obscuring it.
