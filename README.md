# AZQ

AZQ is a system for turning human thought into durable work.

It is built around a simple rule of craft: ideas are gathered, given purpose, shaped into structure, turned into work, and kept with visible evidence on disk.

The repository is organized as a small set of engines, each responsible for one stage in that craft pipeline.

---

## The Rule of Craft

AZQ follows five stages:

| Rule | Meaning |
| ---- | ------- |
| **Cole Scintilla** | Gather sparks |
| **Respice Finem** | Define goals |
| **Strue Formam** | Build deliverables and maps |
| **Age Agenda** | Execute work |
| **Custodi Domum** | Maintain and archive the system |

The filesystem is intended to teach this architecture directly:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
```

---

## Live Baseline

The current repository has the first three live craft layers implemented:

```text
capture -> spark -> goal -> deliverable -> map -> task -> dag
```

That means:

* **Cole Scintilla** is live for capture and spark storage
* **Respice Finem** is live for goal creation and listing
* **Strue Formam** is live for canonical deliverable and goal-map storage
* **Age Agenda** is live for canonical file-backed task, DAG, and task-log storage
* **Custodi Domum** remains a later architectural stage rather than an active operator

The active Stage 1, Stage 2, and Stage 3 storage model is file-backed.
Canonical Finis goals live as one file per goal under `data/finis/goals/`.
`data/finis/goals.json` is legacy migration input only and should not be treated as the active system of record.
Canonical Formam deliverables live as one file per deliverable under `data/form/deliverables/`.
Canonical Formam goal maps live as one file per goal under `data/form/maps/`.
Canonical Agenda task records live as one file per task under `data/agenda/tasks/`.
Canonical Agenda DAG artifacts live as one file per goal under `data/agenda/dags/`.
Canonical Agenda task logs live as one file per task under `data/agenda/logs/`.

---

## Canonical Storage

The visible source of truth lives in the repository tree:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
data/finis/goals/
data/form/deliverables/
data/form/maps/
data/agenda/tasks/
data/agenda/dags/
data/agenda/logs/
```

Finis goal files are human-readable Markdown records such as:

```text
data/finis/goals/FINIS_001.md
data/finis/goals/FINIS_002.md
```

Each canonical goal record exposes the Stage 1 fields:

* `goal_id`
* `title`
* `status`
* `created`
* `description`
* `derived_from`

Where older data used a `goal` field, Stage 1 normalizes that into the canonical `title`.

Formam adds canonical Stage 2 records such as:

```text
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_FINIS_001_MAP.md
```

`data/form/deliverables/` and `data/form/maps/` are the canonical Stage 2 system of record.
Operators should inspect those files directly when they need to verify the live deliverable set or the current goal-level dependency map.

Agenda adds canonical Stage 3 records such as:

```text
data/agenda/tasks/TASK_001.md
data/agenda/dags/GOAL_FINIS_001_DAG.json
data/agenda/logs/TASK_001_LOG.md
```

`data/agenda/tasks/`, `data/agenda/dags/`, and `data/agenda/logs/` are the canonical Stage 3 system of record.
Operators should inspect those files directly when they need to verify the live task set, the current goal-level Agenda DAG, or durable task-log evidence.

---

## Repository Structure

```text
azq/
  azq/
    scintilla/
    finis/
    formam/
    cli.py
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
```

Code lives in `azq/`.
Visible craft artifacts live in `data/`.

---

## Basic Use

Install in editable mode:

```bash
python -m pip install -e .
```

Run the current live commands:

```bash
azq capture
azq sparks
azq fine
azq goal add
azq goals
azq form build <goal_id>
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
azq agenda build <deliverable_id>
azq agenda list
azq agenda show <task_id>
azq agenda dag <deliverable_id>
```

After creating a goal, the durable proof should be a goal file in `data/finis/goals/`, not a write to `data/finis/goals.json`.
After building form, the durable proof should be a deliverable file in `data/form/deliverables/` and a goal map in `data/form/maps/`.
After building agenda for a deliverable, the durable proof should be one or more task files in `data/agenda/tasks/` and a goal-level DAG artifact in `data/agenda/dags/`.
Task-log evidence belongs under `data/agenda/logs/` when Agenda work-log entries are written.

---

## Status

AZQ is in early development.
Stage 1 normalized Finis storage so later engines could depend on canonical file-backed goals without transitional glue.
Stage 2 now uses canonical file-backed Formam records as the live baseline for deliverables and goal maps.
Stage 3 now uses canonical file-backed Agenda records as the live baseline for tasks, DAG artifacts, and task logs.
