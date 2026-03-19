# AZQ Filesystem Model

## Purpose

This document defines the on‑disk structure of the AZQ system.

The filesystem layout mirrors the intellectual pipeline of AZQ. Each stage of the craft process has a corresponding location on disk where its artifacts are stored. This allows the system to remain transparent, inspectable, and resilient.

The guiding principle is simple:

> The filesystem should teach the architecture.

Anyone browsing the repository should be able to understand how ideas move through the system simply by reading the directory tree.

---

# Root Repository Layout

```
azq/
  README.md
  AZQ_PHILOSOPHY.md
  AZQ_CRAFT_CHARTER.md
  AZQ_ENGINE_SPEC.md
  AZQ_FILESYSTEM_MODEL.md
  azq/
  data/
  logs/
  scripts/
  tests/
```

## Explanation

| Directory  | Purpose                                   |
| ---------- | ----------------------------------------- |
| `azq/`     | Source code for AZQ engines               |
| `data/`    | All artifacts produced by the engines     |
| `logs/`    | Operational logs                          |
| `scripts/` | Helper automation and maintenance scripts |
| `tests/`   | Unit and integration tests                |

The repository intentionally separates **code** from **artifacts**.

---

# Source Code Layout

All live engine implementations in this repository live under `azq/`.

```
azq/
  __init__.py
  cli.py
  scintilla/
  finis/
  formam/
  agenda/
```

## Engine Modules

| Module      | Role                            |
| ----------- | ------------------------------- |
| `scintilla` | Capture sparks                  |
| `finis`     | Define goals                    |
| `formam`    | Build structural deliverables   |
| `agenda`    | Manage executable tasks         |

Each module should remain small and focused.
`domum` remains planned, but it is not present in the live repository tree yet.

---

# Data Layer

The `data/` directory mirrors the AZQ craft pipeline.

```
data/

  scintilla/
  finis/
  form/
  agenda/
  artifacts/
  archive/
```

Each directory represents a stage in the lifecycle of work.

---

# Scintilla Storage

Sparks originate here.

```
data/scintilla/

  audio/
  transcripts/
  sparks/
```

## Files

```
audio/
  YYYY-MM-DD_HHMM.wav

transcripts/
  YYYY-MM-DD_HHMM.txt

sparks/
  YYYY-MM-DD_HHMM.json
```

Pipeline:

```
audio -> transcript -> sparks
```

---

# Finis Storage

Goals derived from sparks are stored here.

```
data/finis/

  goals/
  reviews/
```

Example:

```
goals/
  FINIS_001.md
  FINIS_002.md
```

A goal file contains:

```
id
title
description
status
priority
linked_sparks
created_date
```

---

# Formam Storage

Structural deliverables live here.

```
data/form/

  deliverables/
  maps/
```

Examples:

```
deliverables/
  DELIV_audio_cleaner.md
  DELIV_spark_indexer.md
```

Maps describe relationships between deliverables.

```
maps/
  GOAL_FINIS_001_MAP.md
```

---

# Agenda Storage

Executable tasks are managed here.

```
data/agenda/

  tasks/
  dags/
  logs/
```

Example:

```
tasks/
  TASK_001.md
  TASK_002.md
```

DAG files describe execution dependencies.

```
dags/
  FINIS_001_dag.json
```

---

# Artifact Storage

Artifacts created by completed work live here.

```
data/artifacts/

  code/
  notes/
  docs/
  modules/
```

Artifacts represent completed outcomes of goals and deliverables.

---

# Archive

Finished or abandoned material moves here.

```
data/archive/

  goals/
  tasks/
  sparks/
  artifacts/
```

Nothing should disappear silently. Archiving preserves history while keeping the active workspace clean.

---

# Logs

System logs live outside the craft pipeline.

```
logs/

  capture.log
  transcription.log
  agenda.log
  maintenance.log
```

Logs help diagnose operational problems without polluting artifact directories.

---

# Scripts

Automation helpers.

```
scripts/

  daily_review.py
  archive_cleanup.py
  goal_report.py
```

These scripts perform maintenance tasks that do not belong inside engine modules.

---

# Tests

```
tests/

  test_scintilla.py
  test_finis.py
  test_formam.py
```

Every engine should have test coverage.

---

# Example Repository Tree

```
azq/
  README.md
  AZQ_PHILOSOPHY.md
  AZQ_CRAFT_CHARTER.md
  AZQ_ENGINE_SPEC.md
  AZQ_FILESYSTEM_MODEL.md
  azq/
    __init__.py
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
    artifacts/
    archive/
  logs/
  scripts/
  tests/
```

---

# Design Principles

### Transparency

Intermediate artifacts remain visible and inspectable.

### Durability

The system favors plain files:

```
markdown
json
csv
```

### Simplicity

Directories should remain shallow and understandable.

### Reversibility

Work should be traceable backward:

```
task -> deliverable -> goal -> spark
```

---

# Implementation Note

When initializing a new AZQ repository, the following directories can be safely created immediately:

```
data/scintilla/audio
data/scintilla/transcripts
data/scintilla/sparks

data/finis/goals

data/form/deliverables
data/form/maps

data/agenda/tasks
data/agenda/dags
data/agenda/logs

data/artifacts

data/archive

logs
scripts
tests
```

This creates a ready-to-use scaffold for the visible AZQ pipeline in the current repository layout under `azq/`.
Later stages may add more code modules, but the live package root remains `azq/`.

---

# Closing

The filesystem is the skeleton of the system.

If the structure is clear, the system remains understandable even as it grows. If the structure becomes chaotic, the system will eventually collapse under its own weight.

AZQ therefore treats the filesystem not as a storage convenience, but as a visible expression of the craft process itself.
