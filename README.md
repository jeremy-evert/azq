# AZQ

AZQ is a filesystem-backed craft pipeline for turning early thought into durable work.

It is built around a simple rule:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
````

In the current live repository, AZQ can already carry work through the first visible baseline:

```text
spark -> goal -> deliverable -> task -> dag
```

The code lives under `azq/`.
The visible system of record lives under `data/`.

If you can inspect the files on disk, you can inspect what AZQ believes is true.

---

## The Five Engines

AZQ is organized around five public craft layers:

| Craft layer | Meaning                                  | Live today          |
| ----------- | ---------------------------------------- | ------------------- |
| `Scintilla` | gather sparks                            | yes                 |
| `Finis`     | shape goals                              | yes, basic baseline |
| `Formam`    | shape deliverables and maps              | yes, basic baseline |
| `Agenda`    | shape executable work                    | yes, basic baseline |
| `Domum`     | steward, archive, review, status, doctor | not yet             |

These names are not decoration.
They are the intended order of work.

AZQ is trying to keep you from jumping straight from a vague idea to an undifferentiated task list.

---

## What Is Live Now

The current baseline is real code, not just planning docs:

* `azq/scintilla/` captures audio, writes transcripts, and extracts spark records
* `azq/finis/` stores canonical goal files under `data/finis/goals/`
* `azq/formam/` builds canonical deliverables and goal maps under `data/form/`
* `azq/agenda/` builds canonical tasks, goal-level DAG artifacts, and task logs under `data/agenda/`

What is **not** live yet:

* `Domum`
* `azq status`
* `azq doctor`
* archive-first replacement for every destructive path
* the deeper LLM-assisted shaping behavior planned for Finis, Formam, and Agenda

`azq spark rm <id>` is still live today, but it remains a temporary destructive path rather than the desired final stewardship model.

---

## Repository Layout

The live package root is:

```text
azq/
```

The current visible craft records live under:

```text
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

### Practical meaning

* `data/scintilla/` is the spark layer: audio, transcript, and extracted spark JSON
* `data/finis/goals/` is the canonical goal store
* `data/form/deliverables/` and `data/form/maps/` are the canonical Formam records
* `data/agenda/tasks/`, `data/agenda/dags/`, and `data/agenda/logs/` are the canonical Agenda records

Typical filenames look like this:

```text
data/scintilla/sparks/2026-03-09_090255.json
data/finis/goals/FINIS_001.md
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_FINIS_001_MAP.md
data/agenda/tasks/TASK_001.md
data/agenda/dags/GOAL_FINIS_001_DAG.json
data/agenda/logs/TASK_001_LOG.md
```

High-signal support material now lives under:

```text
docs/architecture/
planning/
codex/
attic/
```

---

## Command Quick Reference

These are the live commands exposed by the repository today.

### Scintilla

```bash
azq capture
azq sparks
azq spark <spark_id>
azq spark search "<text>"
azq spark rm <spark_id>
```

* `azq capture` starts the interactive audio capture loop, then writes audio, transcript, and spark artifacts
* `azq sparks` lists saved spark bundles
* `azq spark <spark_id>` shows one exact spark bundle
* `azq spark search "<text>"` searches extracted spark text
* `azq spark rm <spark_id>` deletes that spark bundle

### Finis

```bash
azq fine
azq goals
azq goal add
azq goal close <goal_id>
azq goal archive <goal_id>
```

* `azq fine` reads sparks and proposes candidate goals through the current interactive flow
* `azq goals` lists active goals
* `azq goal add` creates a goal manually
* `azq goal close <goal_id>` marks a goal completed
* `azq goal archive <goal_id>` marks a goal archived

### Formam

```bash
azq form build <goal_id>
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
```

* `azq form build <goal_id>` creates the current first-form baseline for a goal
* `azq form list` lists deliverables
* `azq form show <deliverable_id>` shows one deliverable
* `azq form map <goal_id>` refreshes and prints the goal map path

### Agenda

```bash
azq agenda build <deliverable_id>
azq agenda list
azq agenda show <task_id>
azq agenda dag <deliverable_id>
```

* `azq agenda build <deliverable_id>` creates the current canonical task baseline for one deliverable
* `azq agenda list` lists canonical tasks
* `azq agenda show <task_id>` shows one canonical task
* `azq agenda dag <deliverable_id>` refreshes the parent goal DAG reached from that deliverable

---

## Quickstart

Create and activate a virtual environment, then install AZQ in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Check the live CLI:

```bash
azq
```

You should see the current command list beginning with `capture`, `sparks`, and `spark <id>`, and ending with the `agenda ...` commands.

If you want the smallest reliable proof-of-life path, see [`docs/architecture/AZQ_BOOTSTRAP.md`](docs/architecture/AZQ_BOOTSTRAP.md).

---

## Smallest Proof Of Life

This is the shortest good path to prove the current live baseline without requiring microphone capture.

### 1. Create a goal

```bash
azq goal add
azq goals
```

Example title:

```text
Bootstrap the current AZQ repository
```

You should now have a goal file such as:

```text
data/finis/goals/FINIS_001.md
```

### 2. Build the first deliverable and map

```bash
azq form build FINIS_001
azq form list
azq form show DELIV_001
azq form map FINIS_001
```

You should now have:

```text
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_FINIS_001_MAP.md
```

### 3. Build the first task and DAG

```bash
azq agenda build DELIV_001
azq agenda list
azq agenda show TASK_001
azq agenda dag DELIV_001
```

You should now have:

```text
data/agenda/tasks/TASK_001.md
data/agenda/dags/GOAL_FINIS_001_DAG.json
```

At that point, the current live AZQ baseline is working.

---

## Optional Full Spark Proof

If your microphone and Whisper stack are working, you can prove Scintilla too.

```bash
azq capture
```

Inside the capture loop:

1. start recording
2. say one short idea aloud
3. stop recording
4. wait for transcription and extraction
5. exit cleanly

Then inspect the spark layer:

```bash
azq sparks
azq spark <spark_id>
azq spark search "<text>"
```

If successful, you should see a spark bundle written under:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
```

---

## One Guided Example: Graphite As A Spark

Graphite is **not** a live AZQ engine.

Here, Graphite is used as a serious example project:

* a local-first research and thinking tool
* a workflow that combines local hardware, LLMs, and research pipelines
* a way to produce documented, source-aware, actionable understanding on focused topics

The point of this example is to use the current AZQ baseline to shape Graphite into visible work.

### 1. Define the goal

You can either promote a spark through `azq fine` or create the goal directly:

```bash
azq goal add
```

Example goal title:

```text
Stabilize Graphite MVP around document triage and source-aware ranking
```

Example description:

```text
Use the current Graphite repository to define and build the smallest working research pipeline that, given a directory of documents, identifies which ones matter most and explains why.
```

List goals:

```bash
azq goals
```

### 2. Build form

```bash
azq form build FINIS_001
azq form list
azq form show DELIV_001
azq form map FINIS_001
```

This creates the first visible structural artifact for the goal.

### 3. Build agenda

```bash
azq agenda build DELIV_001
azq agenda list
azq agenda show TASK_001
azq agenda dag DELIV_001
```

This creates the current executable-work baseline.

### 4. Inspect the truth on disk

Check:

```text
data/finis/goals/FINIS_001.md
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_FINIS_001_MAP.md
data/agenda/tasks/TASK_001.md
data/agenda/dags/GOAL_FINIS_001_DAG.json
```

At that point, Graphite has moved through the live AZQ path:

```text
spark -> goal -> deliverable -> task -> dag
```

That is enough to prove that AZQ can hold the shape of real work before the deeper shaping layers are added.

---

## What AZQ Is Becoming Next

The near-term direction is:

1. deepen **Finis** into an LLM-assisted goal-shaping layer
2. deepen **Formam** into an LLM-assisted deliverable-shaping layer
3. deepen **Agenda** into an LLM-assisted task-and-Codex layer
4. implement **Domum**
5. add repository-wide `status` and `doctor`
6. remove destructive delete paths

That order matters.

AZQ is not trying to bolt intelligence on from the outside.
It is trying to deepen the existing craft layers so the engines mean what their names imply.

---

## Reading Guide

If you want the shortest route into the repository:

* start here in `README.md`
* use `docs/architecture/AZQ_BOOTSTRAP.md` to prove the live baseline
* use `docs/architecture/AZQ_COMMAND_MODEL.md` to understand the CLI shape
* use `docs/architecture/AZQ_ENGINE_SPEC.md` to understand what each engine owns
* use `docs/architecture/AZQ_FILESYSTEM_MODEL.md` to understand where artifacts live
* use `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md` to understand what comes next
* use `docs/architecture/AZQ_PHILOSOPHY.md` only when you want the deeper why

---

## Closing

AZQ is not trying to be a generic todo app.

It is trying to become a craft system that:

* gathers sparks without losing them
* shapes goals before they become slogans
* shapes deliverables before they explode into tasks
* shapes executable work before it dissolves into chaos
* eventually preserves and reviews what was built

Right now, the live baseline is smaller than that full ambition.

That is okay.

The important thing is that the current baseline is real, inspectable, and running.
