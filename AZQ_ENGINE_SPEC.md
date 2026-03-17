# AZQ Engine Specification

## Purpose

This document defines the operational behavior of the five engines of AZQ.

Where the Craft Charter defines principles, the Engine Specification defines:

- system inputs
- system outputs
- file artifacts
- command behaviors
- expected failure modes

The specification should remain practical, inspectable, and implementation-neutral where possible.

---

# Global Architectural Model

AZQ transforms observation into artifacts through a staged pipeline.

```

world
↓
observation
↓
sparks
↓
goals
↓
deliverables
↓
tasks
↓
artifacts
↓
archives

```

Each stage is implemented by a corresponding engine.

---

# Engine 1 — Cole Scintilla

## Role

Capture fleeting ideas and convert them into durable spark records.

## Primary Input

- microphone audio
- text entry
- quick notes
- clipboard capture

## Output Artifacts

```

data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/

```

Typical files:

```

audio/YYYY-MM-DD_HHMM.wav
transcripts/YYYY-MM-DD_HHMM.txt
sparks/YYYY-MM-DD_HHMM.json

```

## Core Responsibilities

1. Record audio quickly
2. Transcribe audio using Whisper
3. Extract atomic idea fragments
4. Store fragments as sparks

## CLI Commands

```

azq capture
azq sparks
azq spark show <id>

```

## System Guarantees

- capture latency must be minimal
- sparks must be searchable
- capture must not require goal definition

## Failure Modes

| Failure | Result |
|-------|-------|
| capture friction too high | ideas never recorded |
| sparks not searchable | sparks become dead storage |
| premature judgment | sparks never form |

---

# Engine 2 — Respice Finem

## Role

Transform sparks into goals.

## Primary Inputs

```

data/scintilla/sparks/
data/scintilla/transcripts/

```

## Output Artifacts

```

data/finis/goals/

```

Example:

```

FINIS_001.md
FINIS_002.md

```

## Goal Record Structure

```

id
title
description
status
priority
linked_sparks
created_date

```

## CLI Commands

```

azq goals
azq goals review
azq goal create
azq goal archive

```

## Responsibilities

- cluster related sparks
- elevate meaningful sparks to goals
- clarify desired outcome
- prevent spark hoarding

## Failure Modes

| Failure | Result |
|-------|-------|
| spark overload | noise accumulation |
| vague goals | later structural confusion |

---

# Engine 3 — Strue Formam

## Role

Transform goals into structural deliverables.

## Inputs

```

data/finis/goals/
repository context

```

## Output Artifacts

```

data/form/deliverables/
data/form/maps/

```

Examples:

```

DELIV_audio_cleaner.md
DELIV_spark_indexer.md

```

## Deliverable Structure

```

deliverable_id
goal_id
artifact_description
dependencies
estimated complexity

```

## CLI Commands

```

azq form build <goal>
azq form list
azq form show <deliverable>

```

## Responsibilities

- identify artifacts
- map dependencies
- prevent premature tasks
- define boundaries of work

## Failure Modes

| Failure | Result |
|-------|-------|
| skipping form stage | chaotic task lists |
| vague deliverables | incomplete artifacts |

---

# Engine 4 — Age Agenda

## Role

Convert deliverables into executable tasks.

## Inputs

```

data/form/deliverables/

```

## Outputs

```

data/agenda/tasks/
data/agenda/dags/
data/agenda/logs/

```

Example:

```

TASK_001.md
TASK_002.md

```

## Task Structure

```

task_id
deliverable_id
description
dependencies
status
execution_notes

```

## CLI Commands

```

azq agenda
azq task start
azq task complete
azq task list

```

## Responsibilities

- break deliverables into tasks
- maintain execution order
- track work progress
- integrate with coding assistants

## Failure Modes

| Failure | Result |
|-------|-------|
| tasks detached from deliverables | meaningless activity |
| hidden progress | lost momentum |

---

# Engine 5 — Custodi Domum

## Role

Maintain the health and clarity of the system.

## Inputs

```

completed goals
completed tasks
archivable artifacts

```

## Outputs

```

data/archive/
data/reports/

```

## CLI Commands

```

azq archive
azq prune
azq review

```

## Responsibilities

- archive finished work
- prune abandoned ideas
- generate system health reports
- maintain discoverable knowledge

## Failure Modes

| Failure | Result |
|-------|-------|
| archive friction | clutter accumulation |
| lack of pruning | system entropy |

---

# Global System Properties

## Inspectability

Intermediate artifacts must be visible.

## Plain Files

The system favors durable formats:

```

markdown
json
csv

```

## Reversible Flow

Users must be able to revisit earlier stages.

Example:

```

goal → spark
deliverable → goal
task → deliverable

```

---

# System Boundary

AZQ assists thinking but does not replace judgment.

The user remains responsible for:

- deciding what matters
- rejecting weak ideas
- determining what deserves to exist
```