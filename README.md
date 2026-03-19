# AZQ

AZQ is a filesystem-backed craft pipeline for turning an early idea into visible work.

Today, the live repository can carry work through four concrete layers:

```text
spark -> goal -> deliverable -> task
```

The code lives under `azq/`. The visible system of record lives under `data/`. You can inspect the repository tree directly and see what AZQ believes is true.

## The Rule Of Craft

AZQ is organized around a simple sequence:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
```

In the current repo, that maps to these craft layers:

| Craft layer | Meaning | Live today |
| --- | --- | --- |
| `Scintilla` | capture sparks | yes |
| `Finis` | turn sparks into goals | yes |
| `Formam` | shape goals into deliverables and maps | yes |
| `Agenda` | turn deliverables into tasks and DAGs | yes |
| `Domum` | stewardship, archive, doctor, status | not yet |

The important constraint is order. AZQ is trying to keep you from jumping straight from a vague idea to an undifferentiated task list.

## What Is Live Now

The current baseline is real code, not just planning docs:

- `azq/scintilla/` captures audio, writes transcripts, and extracts spark records.
- `azq/finis/` stores one goal per Markdown file under `data/finis/goals/`.
- `azq/formam/` builds stub deliverables and goal maps under `data/form/`.
- `azq/agenda/` builds stub tasks and goal-level DAG artifacts under `data/agenda/`.

What is not live yet:

- `Domum`
- `azq status`
- `azq doctor`
- a live Graphite engine or Graphite command family

`azq spark rm <id>` is live, but it is still a destructive delete path. The longer-range docs already point away from that and toward archive-first behavior later.

## Repository And Storage Layout

The live package root is `azq/`.

The current visible craft records live under `data/`:

```text
data/
  scintilla/
    audio/
    transcripts/
    sparks/
  finis/
    goals/
    goals.json
  form/
    deliverables/
    maps/
  agenda/
    tasks/
    dags/
    logs/
```

Practical notes:

- `data/scintilla/` is the spark layer: audio, transcript, and extracted spark JSON.
- `data/finis/goals/` is the canonical goal store.
- `data/finis/goals.json` is legacy migration input, not the active goal store.
- `data/form/deliverables/` and `data/form/maps/` are the canonical Formam records.
- `data/agenda/tasks/`, `data/agenda/dags/`, and `data/agenda/logs/` are the canonical Agenda records.

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

## Command Quick Reference

These are the live commands exposed by the repo today.

### Scintilla

```bash
azq capture
azq sparks
azq spark <spark_id>
azq spark search "<text>"
azq spark rm <spark_id>
```

- `azq capture` starts the interactive audio capture loop. It records audio, runs Whisper transcription, then extracts sparks into JSON.
- `azq sparks` lists saved spark bundles in filename order.
- `azq spark <spark_id>` shows the transcript, extracted sparks, and file paths for one exact spark id.
- `azq spark search "<text>"` searches extracted spark text.
- `azq spark rm <spark_id>` deletes that spark bundle's audio, transcript, and spark JSON.

### Finis

```bash
azq fine
azq goals
azq goal add
azq goal close <goal_id>
azq goal archive <goal_id>
```

- `azq fine` reads sparks, proposes candidate goals, and interactively asks which ones to accept.
- `azq goals` lists active goals from canonical goal files.
- `azq goal add` creates a goal manually by prompting for title and optional description.
- `azq goal close <goal_id>` marks a goal `completed`.
- `azq goal archive <goal_id>` marks a goal `archived`.

### Formam

```bash
azq form build <goal_id>
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
```

- `azq form build <goal_id>` creates one stub deliverable for an active goal and refreshes that goal's map.
- `azq form list` lists deliverables.
- `azq form show <deliverable_id>` shows one deliverable record.
- `azq form map <goal_id>` refreshes and prints the goal map path for that goal.

### Agenda

```bash
azq agenda build <deliverable_id>
azq agenda list
azq agenda show <task_id>
azq agenda dag <deliverable_id>
```

- `azq agenda build <deliverable_id>` creates one stub task for that deliverable.
- `azq agenda list` lists canonical tasks.
- `azq agenda show <task_id>` shows one task record.
- `azq agenda dag <deliverable_id>` refreshes the goal-level DAG artifact derived from that deliverable's parent goal.

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

You should see the current command list beginning with `capture`, `sparks`, `spark <id>`, and ending with the `agenda ...` commands.

If you want to verify the storage tree exists, run:

```bash
find data -maxdepth 3 -type d | sort
```

If you plan to use `azq capture`, you need:

- a working microphone
- the Python audio stack from the project dependencies
- local Whisper model loading (`openai-whisper`)

## Guided Walkthrough: Capture The Spark Of Graphite

Graphite is not a live AZQ engine. In this README, Graphite is a serious example spark:

- a local-first research and thinking tool
- a workflow that combines local hardware, LLMs, and research pipelines
- a way to produce documented, source-aware, actionable understanding on focused topics

The point of this walkthrough is to use the live AZQ pipeline to shape that idea into visible work.

### 1. Capture Or Inspect The Spark

If you have a microphone available, start with live capture:

```bash
azq capture
```

Inside the current capture flow, start recording, speak a short Graphite idea, enter `2` to stop recording, wait for transcription and spark extraction to finish, then enter `4` to exit the loop.

Something simple is enough:

```text
Graphite could be a local research system that uses LLMs and documented pipelines
to produce source-aware technical understanding with lower friction.
```

You should now see new files under:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
```

To inspect what was captured:

```bash
azq sparks
azq spark <spark_id>
```

`azq sparks` gives you the available spark ids. `azq spark <spark_id>` lets you inspect the transcript, extracted spark lines, and the exact artifact paths on disk.

Truth check on disk:

- `data/scintilla/audio/<spark_id>.wav`
- `data/scintilla/transcripts/<spark_id>.txt`
- `data/scintilla/sparks/<spark_id>.json`

If you already have sparks and want to find the Graphite-shaped one:

```bash
azq spark search "graphite"
```

That searches the extracted spark text, not the goal layer.

### 2. Promote The Spark Into A Goal

Use the live interactive goal-promoter:

```bash
azq fine
```

`azq fine` scans spark files, proposes candidate goals, and asks you whether to accept them. If your Graphite spark is distinct enough, accept it with `y`.

You should now see a canonical goal file such as:

```text
data/finis/goals/FINIS_028.md
```

List active goals:

```bash
azq goals
```

If you want to create the Graphite goal manually instead of going through `fine`, use:

```bash
azq goal add
```

Then enter a title and optional description when prompted.

A practical Graphite title might be:

```text
Define Graphite as a local source-aware research workflow
```

Truth check on disk:

- inspect `data/finis/goals/<goal_id>.md`
- confirm `derived_from` points back to the spark id if the goal came from `azq fine`

### 3. Build The First Deliverable From The Goal

Once you have the Graphite goal id, build form:

```bash
azq form build <goal_id>
```

Example:

```bash
azq form build FINIS_028
```

This creates one stub deliverable for the goal and refreshes the goal map. In the current repo, `form build` is intentionally conservative: it does not generate a whole plan tree, it writes the first visible structural artifact.

You should now see output that names both files:

```text
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_<goal_id>_MAP.md
```

Inspect the deliverable set:

```bash
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
```

- `azq form list` helps you grab the deliverable id.
- `azq form show <deliverable_id>` shows the deliverable's title, status, description, and dependencies.
- `azq form map <goal_id>` refreshes the goal map again and prints its path.

Truth check on disk:

- `data/form/deliverables/<deliverable_id>.md`
- `data/form/maps/GOAL_<goal_id>_MAP.md`

### 4. Build Agenda Tasks From One Deliverable

Pick the Graphite deliverable id and build the first task:

```bash
azq agenda build <deliverable_id>
```

Example:

```bash
azq agenda build DELIV_001
```

In the current repo, this creates one stub task for that deliverable.

You should now see a task file such as:

```text
data/agenda/tasks/TASK_001.md
```

Inspect the task layer:

```bash
azq agenda list
azq agenda show <task_id>
```

- `azq agenda list` shows task ids, deliverable parents, status, and short descriptions.
- `azq agenda show <task_id>` shows the full task record.

Truth check on disk:

- `data/agenda/tasks/<task_id>.md`

### 5. Refresh And Inspect The DAG

Refresh the Agenda DAG from the deliverable:

```bash
azq agenda dag <deliverable_id>
```

Example:

```bash
azq agenda dag DELIV_001
```

This command takes a deliverable id, but the artifact it writes is goal-scoped. That is the current live behavior in the repo.

You should now see a DAG file such as:

```text
data/agenda/dags/GOAL_<goal_id>_DAG.json
```

Truth check on disk:

- open `data/agenda/dags/GOAL_<goal_id>_DAG.json`
- confirm it names the parent goal, the deliverable id, and the current task ids

At that point, Graphite has moved through the live AZQ craft baseline:

```text
spark -> goal -> deliverable -> task -> dag
```

## Graphite As An Emerging Idea

Graphite is not implemented here as an engine, subsystem, or command family.

Right now, Graphite is better treated as:

- a spark worth capturing
- a candidate project worth defining carefully
- a serious test case for whether AZQ's craft flow produces better work

That matters because the workflow comes first. If AZQ can help define Graphite clearly, produce visible deliverables, and derive actionable tasks without collapsing into hand-wavy planning, then a future Graphite engine has a better chance of being real and coherent.

## What Comes Next

The near-term architectural direction in the docs is clear:

- preserve the live Scintilla, Finis, Formam, and Agenda baselines
- add `Domum`
- add archive-first stewardship
- add repository-wide `status` and `doctor`
- reduce or remove destructive delete paths like `azq spark rm`

Those are next-step directions, not claims about what already exists in this checkout.
