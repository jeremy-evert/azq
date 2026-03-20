# AZQ Command Model

## Purpose

This document defines the public command-line model for AZQ.

The command model should do two jobs well:

1. describe the **current live operator surface**
2. define the **future public direction** without pretending future behavior is already implemented

The CLI is not just a convenience layer.
It is the most visible expression of the craft sequence:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
````

That sequence is carried by the five public craft layers:

* **Scintilla** gathers sparks
* **Finis** shapes goals
* **Formam** shapes deliverables and maps
* **Agenda** shapes executable work
* **Domum** stewards, archives, reviews, and later supports repository health

There is **no sixth public engine** in this command model.

If helper logic is borrowed from other scripts or projects, it should be absorbed into the existing engine structure rather than exposed as a new public command family.

---

## Command Model Principles

All public commands should obey these rules:

### 1. Commands mirror the craft stages

The public CLI should reinforce the real craft pipeline:

```text
Scintilla -> Finis -> Formam -> Agenda -> Domum
```

The CLI must not encourage users to skip from vague idea directly to an undifferentiated task pile.

### 2. Live commands and future commands must be clearly separated

This document must tell the truth about what the repository exposes **now**.

It may also preserve future command direction, but future commands must be labeled clearly as future-facing.
The command model should never teach stale or aspirational commands as though they are already live.

### 3. Commands should create or inspect durable artifacts

Public commands should create, inspect, refresh, archive, or validate visible filesystem artifacts under `data/`.

Opaque hidden state is a design smell.

### 4. Existing engine names should own future intelligence

Future LLM-assisted shaping work belongs inside:

* **Finis** for goal shaping
* **Formam** for deliverable shaping
* **Agenda** for task shaping, dedupe, DAG work, and Codex preparation

The command model should not split those concerns into unrelated extra public command families.

### 5. Keep the public surface small

A smaller, coherent command model is better than a sprawling maze of almost-synonyms.

---

## Current Live Baseline

The current live baseline is the Stage 1 through Stage 3 craft path proven in bootstrap:

```text
spark -> goal -> deliverable -> task -> dag
```

The current live commands are:

```text
azq capture
azq sparks
azq spark <id>
azq spark search <text>
azq spark rm <id>
azq fine
azq goals
azq goal add
azq goal close <id>
azq goal archive <id>
azq form build <goal_id>
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
azq agenda build <deliverable_id>
azq agenda list
azq agenda show <task_id>
azq agenda dag <deliverable_id>
```

The current canonical storage homes are:

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

That is the live operator truth today.

---

## Public CLI Shape

The public CLI should continue to use this top-level pattern:

```text
azq <stage or singular object> [subcommand] [arguments]
```

Examples from the live system:

```text
azq capture
azq sparks
azq spark <id>
azq goal add
azq form build <goal_id>
azq agenda build <deliverable_id>
```

The command model intentionally mixes:

* **short top-level stage commands** for frequent use
* **singular object subcommands** when an operation targets a specific object

That hybrid shape is acceptable as long as it stays coherent.

---

## 1. Cole Scintilla

Gather sparks.

### Purpose

Scintilla is the intake layer.
It captures or inspects early thought and preserves spark artifacts visibly on disk.

### Live commands

```text
azq capture
azq sparks
azq spark <id>
azq spark search <text>
azq spark rm <id>
```

### Live meanings

#### `azq capture`

Start interactive audio capture, transcription, and spark extraction.

Pipeline:

```text
audio -> transcript -> spark record
```

Artifacts:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
```

#### `azq sparks`

List saved spark bundles.

#### `azq spark <id>`

Inspect one exact spark bundle.

#### `azq spark search <text>`

Search extracted spark text.

#### `azq spark rm <id>`

Remove one spark bundle.

This remains live today, but it is a **temporary destructive path**.
The implementation plan intends to replace destructive removal with archive-first behavior later.

### Future-facing direction

Scintilla may later grow capabilities such as:

```text
azq capture text "..."
azq spark archive <id>
azq spark summarize <id>
```

But Scintilla should remain the **spark layer**, not become a general planning engine.

---

## 2. Respice Finem

Shape goals.

### Purpose

Finis takes sparks and helps the user define ends.

Today, it stores and lists goals.
In the next implementation stages, it should deepen into an LLM-assisted goal-shaping layer that can inspect sparks, ask narrowing questions, and help shape better goals.

### Live commands

```text
azq fine
azq goals
azq goal add
azq goal close <goal_id>
azq goal archive <goal_id>
```

### Live meanings

#### `azq fine`

Read sparks and propose candidate goals through the current interactive flow.

#### `azq goals`

List active goals from canonical goal files.

#### `azq goal add`

Create a goal manually.

#### `azq goal close <goal_id>`

Mark a goal completed.

#### `azq goal archive <goal_id>`

Mark a goal archived.

### Canonical artifacts

```text
data/finis/goals/
```

### Future-facing direction

Future Finis behavior should stay **inside Finis**.

Likely future capabilities include:

```text
azq fine inspect <spark_id>
azq fine shape <spark_id>
azq fine questions <spark_id or goal_id>
azq goal show <goal_id>
```

These future commands should support behavior such as:

* spark review
* narrowing questions
* tractability and usefulness notes
* refined goal proposals
* manifesto or intent-note support attached to goal work

They should not create a separate public planning engine.
They belong to Finis.

---

## 3. Strue Formam

Shape deliverables and maps.

### Purpose

Formam defines what should exist if a goal succeeds.

Today, it builds stub deliverables and goal maps.
In later stages, it should deepen into an LLM-assisted deliverable-shaping layer that can expand, prioritize, and refine deliverables.

### Live commands

```text
azq form build <goal_id>
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
```

### Live meanings

#### `azq form build <goal_id>`

Create the current first-form baseline for a goal:
a deliverable record and a goal map.

#### `azq form list`

List deliverables.

#### `azq form show <deliverable_id>`

Inspect one deliverable.

#### `azq form map <goal_id>`

Refresh or inspect the goal map for one goal.

### Canonical artifacts

```text
data/form/deliverables/
data/form/maps/
```

### Future-facing direction

Future Formam behavior should stay **inside Formam**.

Likely future capabilities include:

```text
azq form expand <goal_id or deliverable_id>
azq form prioritize <goal_id>
```

These future commands should support behavior such as:

* deliverable expansion
* first-now versus later prioritization
* map refinement
* boundary clarification
* proposal artifacts that can later be accepted into canonical Formam storage

Formam should remain the layer that shapes deliverables and maps.
It should not jump directly to executable task decomposition.

---

## 4. Age Agenda

Shape executable work.

### Purpose

Agenda turns deliverables into executable work.

Today, it creates canonical task stubs and goal-level DAG artifacts.
In later stages, it should deepen into the LLM-assisted task-and-Codex layer.

### Live commands

```text
azq agenda build <deliverable_id>
azq agenda list
azq agenda show <task_id>
azq agenda dag <deliverable_id>
```

### Live meanings

#### `azq agenda build <deliverable_id>`

Create or refresh canonical task records for one deliverable.

#### `azq agenda list`

List canonical tasks.

#### `azq agenda show <task_id>`

Inspect one canonical task.

#### `azq agenda dag <deliverable_id>`

Refresh and inspect the parent goal DAG reached from one exact deliverable.

### Canonical artifacts

```text
data/agenda/tasks/
data/agenda/dags/
data/agenda/logs/
```

### Important current constraint

The current live operator surface is the **narrow `azq agenda ...` family**.

Older split families such as:

```text
azq task ...
azq dag ...
```

are **not** the live baseline and should not be taught as current behavior unless later code adds them explicitly.

### Future-facing direction

Future Agenda behavior should remain **inside Agenda**.

Likely future capabilities include:

```text
azq agenda expand <deliverable_id>
azq agenda dedupe <deliverable_id>
azq agenda dag <deliverable_id>
azq agenda codex prepare <deliverable_id>
azq agenda codex run <deliverable_id>
azq agenda codex report <deliverable_id>
```

These future commands should support behavior such as:

* commit-sized task decomposition
* task proposal generation
* task deduplication
* deterministic dependency DAG generation
* Codex preparation
* Codex execution reporting

Agenda should own the bridge from deliverable to executable work.
That includes Codex preparation.
This should not be split into a stray public execution engine.

---

## 5. Custodi Domum

Steward the system.

### Purpose

Domum is the stewardship layer.

It is not live yet.
When implemented, it should archive, review, prune carefully, and later support repository-wide introspection through `status` and `doctor`.

### Live commands

There is **no live Domum command family yet**.

### Future-facing direction

Likely future Domum capabilities include:

```text
azq archive ...
azq prune
azq review
azq status
azq doctor
```

More specific future commands may include:

```text
azq archive spark <id>
azq archive goal <goal_id>
azq archive task <task_id>
```

### Stewardship constraints

Domum should:

* preserve provenance
* move the system toward archive-first behavior
* support visible review
* eventually power repository-wide health and maturity reporting

Domum should not arrive before archive paths exist.
`status` and `doctor` should report what is visibly true from disk, not hidden internal state.

---

## Global Commands

### Live now

No global commands beyond the root CLI listing are part of the stable live surface today.

### Future-facing

These remain long-range public commands once Domum exists:

```text
azq status
azq doctor
azq review
azq version
```

They should be added only when they are backed by real, visible repository evidence.

---

## What The Command Model Should Not Do

The public command model should **not**:

* invent a sixth public engine
* split future task shaping away from Agenda
* split future deliverable shaping away from Formam
* split future goal shaping away from Finis
* teach `azq task ...` and `azq dag ...` as the live baseline today
* hide proposal artifacts in opaque in-memory flows
* encourage destructive deletion as a permanent norm
* grow a command backlog faster than the repository can support

---

## Current Recommended Workflow

### Live baseline workflow today

```text
# gather or inspect sparks
azq capture
azq sparks
azq spark <id>
azq spark search "<text>"

# define a goal
azq fine
azq goal add
azq goals

# build structure
azq form build FINIS_001
azq form list
azq form show DELIV_001
azq form map FINIS_001

# shape current executable work
azq agenda build DELIV_001
azq agenda list
azq agenda show TASK_001
azq agenda dag DELIV_001
```

### Future workflow direction

As later stages land, the workflow should deepen without changing the public craft story:

```text
spark -> Finis shaping -> Formam shaping -> Agenda shaping -> Domum stewardship
```

That means future LLM-assisted expansion, prioritization, decomposition, dedupe, and Codex preparation should appear as richer behavior **inside the existing engines**, not as a new parallel command garden.

---

## Naming Guidance

Use these rules when adding commands later:

* prefer stage-owned commands over generic orphan verbs
* prefer one obvious canonical spelling
* avoid synonym clutter
* prefer inspectable nouns and visible actions
* keep singular object inspection simple
* keep future commands close to current live naming where possible

Good examples:

```text
azq fine
azq form build <goal_id>
azq form expand <goal_id>
azq agenda build <deliverable_id>
azq agenda codex prepare <deliverable_id>
azq archive goal <goal_id>
```

Bad examples:

```text
azq task list
azq planning expand
azq engine codex
azq work generate
```

if those names bypass the craft story or create a second competing mental model.

---

## Closing

The command model is the path system of the craft.

If the paths are clear, the repository stays teachable.
If the paths sprawl, the craft sequence decays.

So the public command model should remain:

* small
* honest
* stage-aligned
* file-backed
* future-aware without pretending
* faithful to the five-engine story

Finis should shape goals.
Formam should shape deliverables.
Agenda should shape executable work.
Domum should steward what remains.

The CLI should make that truth obvious.
