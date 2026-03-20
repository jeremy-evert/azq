# AZQ Bootstrap

## Purpose

This document defines the shortest reliable path from a repository root to a working AZQ instance.

Right now, bootstrap is about proving the **current live baseline**:

```text
spark -> goal -> deliverable -> task -> dag
````

That baseline is implemented through:

* **Scintilla** for spark capture
* **Finis** for canonical goals
* **Formam** for canonical deliverables and goal maps
* **Agenda** for canonical tasks and goal-level DAGs

Bootstrap is intentionally narrow.

It is **not** a full setup guide for later LLM-assisted shaping work inside Finis, Formam, and Agenda.
It is **not** a guide to Domum, `status`, `doctor`, or archive-first stewardship.
Those belong to the implementation plan and later operating docs, not here. 

---

## What Bootstrap Should Prove

A successful bootstrap proves all of the following:

1. the package installs and the `azq` command runs
2. the repository can write canonical craft artifacts under `data/`
3. at least one goal can be created
4. at least one deliverable and one goal map can be created
5. at least one task and one goal-level DAG can be created
6. if audio capture is available, at least one spark can also be captured

That is enough to prove the repository is no longer inert.

---

## Current Live Storage

The current visible system of record is:

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

Canonical records live here:

* `data/finis/goals/` for goals
* `data/form/deliverables/` for deliverables
* `data/form/maps/` for goal maps
* `data/agenda/tasks/` for tasks
* `data/agenda/dags/` for goal-level DAGs
* `data/agenda/logs/` for task logs

That matches the current implementation plan and current Stage 3 baseline. 

---

## Preconditions

Before starting, you should have:

* Python 3
* `venv`
* the repository checked out locally
* a microphone **only if** you want to prove live Scintilla capture during bootstrap

---

## 1. Start At Repository Root

```bash
pwd
ls
```

You should be standing where `pyproject.toml` lives.

---

## 2. Create A Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

---

## 3. Install AZQ In Editable Mode

```bash
python -m pip install -e .
```

Sanity check:

```bash
azq
```

Expected result:

* the `azq` CLI runs
* the current live command surface is printed

At this point, the package is installed but the repository may still have no craft artifacts yet.

---

## 4. Create The Canonical Data Directories

Some repos will already have these.
If not, create them now.

```bash
mkdir -p \
  data/scintilla/audio \
  data/scintilla/transcripts \
  data/scintilla/sparks \
  data/finis/goals \
  data/form/deliverables \
  data/form/maps \
  data/agenda/tasks \
  data/agenda/dags \
  data/agenda/logs
```

Quick proof:

```bash
find data -maxdepth 3 -type d | sort
```

---

## 5. Recommended Fast Bootstrap Path

This is the shortest reliable path to proving the current Finis, Formam, and Agenda baseline.

### Create the first goal

```bash
azq goal add
```

Enter a simple title when prompted.

Example:

```text
Bootstrap the current AZQ repository
```

List goals:

```bash
azq goals
```

You should now have a canonical goal file such as:

```text
data/finis/goals/FINIS_001.md
```

### Build the first deliverable and map

```bash
azq form build FINIS_001
azq form list
azq form show DELIV_001
azq form map FINIS_001
```

You should now have artifacts such as:

```text
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_FINIS_001_MAP.md
```

### Build the first task and DAG

```bash
azq agenda build DELIV_001
azq agenda list
azq agenda show TASK_001
azq agenda dag DELIV_001
```

You should now have artifacts such as:

```text
data/agenda/tasks/TASK_001.md
data/agenda/dags/GOAL_FINIS_001_DAG.json
```

This is enough to prove the current live Finis, Formam, and Agenda chain.

---

## 6. Optional Full Spark Proof

If your microphone and Whisper stack are working, prove Scintilla too.

Run:

```bash
azq capture
```

In the current capture loop:

1. start recording
2. say one short idea aloud
3. stop recording
4. wait for transcription and extraction
5. exit cleanly

If successful, you should see files like:

```text
data/scintilla/audio/YYYY-MM-DD_HHMMSS.wav
data/scintilla/transcripts/YYYY-MM-DD_HHMMSS.txt
data/scintilla/sparks/YYYY-MM-DD_HHMMSS.json
```

Then inspect the spark layer:

```bash
azq sparks
azq spark <spark_id>
azq spark search "<text>"
```

This proves the full live baseline from spark onward.

---

## 7. Proof Of Life

Bootstrap is complete when these commands work:

```bash
azq
azq goals
azq form list
azq agenda list
```

And if Scintilla was included:

```bash
azq sparks
```

And these artifact homes exist on disk:

```text
data/finis/goals/
data/form/deliverables/
data/form/maps/
data/agenda/tasks/
data/agenda/dags/
data/agenda/logs/
```

And optionally:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
```

---

## 8. Smallest Acceptable Bootstrap

If you want the shortest acceptable sequence, use this:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
mkdir -p data/finis/goals data/form/deliverables data/form/maps data/agenda/tasks data/agenda/dags data/agenda/logs
azq goal add
azq goals
azq form build FINIS_001
azq form list
azq agenda build DELIV_001
azq agenda list
azq agenda dag DELIV_001
```

If you also want to prove Scintilla, add:

```bash
azq capture
azq sparks
```

---

## 9. Common Failure Cases

### `azq` does not run

```bash
python -m pip install -e .
which azq
```

### `azq form build <goal_id>` fails

Check:

* the parent goal exists under `data/finis/goals/`
* you used the exact goal id, such as `FINIS_001`

### `azq agenda build <deliverable_id>` fails

Check:

* the parent deliverable exists under `data/form/deliverables/`
* you used the exact deliverable id, such as `DELIV_001`

### `azq agenda dag <deliverable_id>` fails

Check:

* the deliverable exists
* the deliverable still points to a valid parent goal
* `data/agenda/dags/` is writable

### `azq capture` fails

Check:

* microphone availability
* host audio permissions
* Whisper dependencies
* whether audio was still written under `data/scintilla/audio/`

Bootstrap should fail loudly instead of pretending success.

---

## 10. After Bootstrap

Once bootstrap succeeds, the next sensible work is:

1. keep building real goals, deliverables, and tasks
2. deepen Finis into an LLM-assisted goal-shaping layer
3. deepen Formam into an LLM-assisted deliverable-shaping layer
4. deepen Agenda into an LLM-assisted task-and-Codex layer
5. implement Domum afterward

That is the order in the current implementation plan. 

---

## Closing

Bootstrap is not the whole system.

It is the first proof that the current AZQ baseline is alive, file-backed, and inspectable.

If the repository can create one goal, one deliverable, one task, and one DAG under the canonical storage homes, then AZQ is genuinely running.
If Scintilla can also capture one spark, the full current live craft path is proven too.

That is enough.

Anything deeper belongs in the implementation plan, README, or later operating documents, not in bootstrap.
