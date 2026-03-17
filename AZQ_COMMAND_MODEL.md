# AZQ Command Model

## Purpose

This document defines the command-line interface for AZQ.

The command model is the primary way users interact with the system.  
It exposes the five engines of AZQ as a small, memorable set of commands.

The CLI must obey the Craft Charter:

- stages remain distinct
- commands remain simple
- every command produces or modifies a visible artifact
- no command should bypass the craft pipeline

The command model mirrors the AZQ flow:

```

spark → goal → deliverable → task → artifact → archive

```

---

# CLI Philosophy

The AZQ CLI follows three rules.

### 1 — Commands mirror the craft stages

Each command group corresponds to an engine.

```

spark
goal
form
task
archive

```

This keeps the user mentally aligned with the craft process.

---

### 2 — Commands are short and memorable

Commands should feel like natural verbs.

Good command design helps memory and reduces friction.

Examples:

```

azq capture
azq sparks
azq goals
azq form
azq task

```

---

### 3 — Commands create durable artifacts

Every command should modify or generate files in `data/`.

Opaque state is avoided.

---

# CLI Structure

General pattern:

```

azq <resource> <verb> [arguments]

```

Examples:

```

azq spark list
azq goal create
azq form build
azq task start

```

---

# Global Commands

These operate across the entire system.

```

azq status
azq doctor
azq review
azq version

```

### azq status

Shows pipeline status across stages.

Example output:

```

sparks:       37
goals:        5 active
deliverables: 12
tasks:        9 open

```

---

### azq doctor

Checks repository health.

Validates:

- directory structure
- missing files
- corrupted artifacts
- configuration problems

---

### azq review

Produces a summary of recent activity.

Typical use:

```

azq review
azq review weekly

```

---

# Engine Commands

## 1. Cole Scintilla

Gather sparks.

### Capture

```

azq capture

```

Starts audio capture and transcription.

Pipeline:

```

audio → transcript → sparks

```

Artifacts created:

```

data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/

```

---

### Capture Text

```

azq capture text "note"

```

Creates a spark directly from text.

---

### List Sparks

```

azq sparks

```

Shows recent sparks.

---

### Inspect Spark

```

azq spark show <id>

```

---

### Search Sparks

```

azq spark search <text>

```

---

### Remove Spark

```

azq spark rm <id>

```

---

# 2. Respice Finem

Define goals.

### List Goals

```

azq goals

```

---

### Review Goals

```

azq goals review

```

---

### Create Goal

```

azq goal create

```

Creates a goal from selected sparks.

Artifacts:

```

data/finis/goals/

```

---

### Show Goal

```

azq goal show <goal_id>

```

---

### Link Sparks

```

azq goal link-sparks <goal_id> <spark_ids>

```

---

### Close Goal

```

azq goal close <goal_id>

```

---

# 3. Strue Formam

Build structure.

### Build Form

```

azq form build <goal_id>

```

Produces deliverables.

Artifacts:

```

data/form/deliverables/

```

---

### List Deliverables

```

azq form list

```

---

### Show Deliverable

```

azq form show <deliverable_id>

```

---

### Build Map

```

azq form map <goal_id>

```

Creates dependency structure.

Artifacts:

```

data/form/maps/

```

---

# 4. Age Agenda

Drive the work.

### Show Agenda

```

azq agenda

```

Overview of current tasks.

---

### List Tasks

```

azq task list

```

---

### Start Task

```

azq task start <task_id>

```

---

### Complete Task

```

azq task complete <task_id>

```

---

### Build DAG

```

azq dag build <goal_id>

```

Artifacts:

```

data/agenda/dags/

```

---

### Show DAG

```

azq dag show <goal_id>

```

---

# 5. Custodi Domum

Maintain the system.

### Archive

```

azq archive

```

Moves completed work into archive.

Artifacts:

```

data/archive/

```

---

### Archive Goal

```

azq archive goal <goal_id>

```

---

### Archive Task

```

azq archive task <task_id>

```

---

### Prune

```

azq prune

```

Removes stale sparks and abandoned records.

---

### Health Report

```

azq report health

```

---

# Operational Scripts

Some maintenance tasks run through scripts.

Examples:

```

python scripts/daily_review.py
python scripts/archive_cleanup.py

```

CLI wrappers may call these.

---

# Recommended Daily Workflow

```

# gather

azq capture
azq sparks

# choose ends

azq goals review
azq goal create

# build structure

azq form build FINIS_001

# execute work

azq task list
azq task start TASK_001
azq task complete TASK_001

# maintain system

azq review
azq archive
azq prune

```

---

# Command Backlog

Future commands may include:

```

azq artifact list
azq artifact show
azq spark summarize
azq goal research
azq agenda focus

```

These should only be added if they serve the craft pipeline.

---

# Closing

The command model is the path system of the AZQ garden.

If the paths are clear, users can move naturally from spark to artifact.

If the paths become tangled, the garden becomes unusable.

The CLI should therefore remain:

- small
- memorable
- faithful to the craft sequence

