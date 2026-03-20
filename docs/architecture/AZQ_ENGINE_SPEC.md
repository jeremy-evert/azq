# AZQ Engine Specification

## Purpose

This document defines the operational behavior of the five engines of AZQ.

Where the Craft Charter defines doctrine, and the Command Model defines the public CLI surface, the Engine Specification defines what each engine is responsible for in practical terms:

- primary inputs
- primary outputs
- canonical artifact homes
- live command behavior
- future engine responsibilities
- engine boundaries
- expected failure modes

This document must tell the truth about two things at once:

1. what the repository can do **right now**
2. what each engine is expected to grow into according to the implementation plan

The live package root is `azq/`.
The live Stage 1 through Stage 3 baseline is the filesystem-backed craft path proven by bootstrap:

```text
spark -> goal -> deliverable -> task -> dag
````

The next implementation work deepens the existing engines rather than adding a sixth public craft layer:

* **Finis** deepens into an LLM-assisted goal-shaping layer
* **Formam** deepens into an LLM-assisted deliverable-shaping layer
* **Agenda** deepens into an LLM-assisted task-and-Codex layer
* **Domum** arrives afterward as stewardship and repository introspection

This document is therefore written in two modes:

* **Live now** means behavior the repository currently exposes
* **Future direction** means engine-owned behavior the implementation plan explicitly calls for, but which should not be taught as already live

---

# Global Architectural Model

AZQ transforms observation into durable craft artifacts through a staged filesystem-backed pipeline.

```text
world
-> observation
-> sparks
-> goals
-> deliverables
-> tasks
-> artifacts
-> archives
```

Each transition is owned by one engine.

The engines are:

1. **Cole Scintilla**
2. **Respice Finem**
3. **Strue Formam**
4. **Age Agenda**
5. **Custodi Domum**

There is no sixth public engine in this specification.

If implementation help is borrowed from existing helper scripts, outside projects, or orchestration tools, it should be absorbed into the engine that conceptually owns that behavior.

---

# Global Engine Rules

All engines must obey these rules.

## 1. Durable files first

Every engine should create or inspect visible, durable artifacts under `data/`.

Hidden state is a smell.
Opaque orchestration is a liability.
Intermediate files are a feature, not an embarrassment.

## 2. Later objects require traceable parents

Every later-stage object should point back to an earlier-stage parent.

Examples:

* spark -> optional transcript/audio provenance
* goal -> spark or manual origin
* deliverable -> goal
* task -> deliverable
* DAG -> parent goal reached through deliverables
* archive -> original active artifact provenance

## 3. Proposal artifacts are not canonical artifacts

Future LLM-assisted shaping work should produce **proposal artifacts** before acceptance.

Accepted canonical artifacts belong in the existing craft homes:

* `data/finis/goals/`
* `data/form/deliverables/`
* `data/form/maps/`
* `data/agenda/tasks/`
* `data/agenda/dags/`
* `data/agenda/logs/`

Proposal artifacts may live inside the same engine family, but they must not silently overwrite accepted canonical state.

## 4. Engines should deepen, not split

Future shaping behavior should stay inside the engines that own that stage of craft:

* Finis shapes goals
* Formam shapes deliverables
* Agenda shapes executable work
* Domum stewards and evaluates repository condition

## 5. Archive before deletion

The implementation direction is archive-first stewardship.
Destructive deletion may remain temporarily live in isolated places, but it is not the desired final model.

---

# Engine 1 — Cole Scintilla

## Role

Capture fleeting thought and preserve it as durable spark artifacts.

Scintilla is the intake layer.
It gathers raw material without requiring premature commitment to goals, deliverables, or tasks.

## Primary Inputs

Live now:

* microphone audio

Future direction may also include:

* text entry
* clipboard input
* quick notes

## Canonical Output Artifacts

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
```

Typical files:

```text
data/scintilla/audio/YYYY-MM-DD_HHMMSS.wav
data/scintilla/transcripts/YYYY-MM-DD_HHMMSS.txt
data/scintilla/sparks/YYYY-MM-DD_HHMMSS.json
```

## Live Commands

```text
azq capture
azq sparks
azq spark <id>
azq spark search <text>
azq spark rm <id>
```

## Live Responsibilities

* record audio
* transcribe audio
* extract spark records
* list and inspect spark bundles
* search spark text
* support exact-id inspection of a spark bundle

## Live Guarantees

* spark capture should not require a goal first
* spark inspection should remain possible from the filesystem and the CLI
* audio, transcript, and spark JSON for one capture should remain traceable as one bundle

## Future Direction

Scintilla may deepen later, but it should remain the spark layer.

Reasonable future capabilities include:

* text-native capture
* summary views for a spark bundle
* archive-first spark retirement

Scintilla should **not** become the place where full planning, task decomposition, or research orchestration lives.

## Failure Modes

| Failure                                            | Result                                |
| -------------------------------------------------- | ------------------------------------- |
| capture friction too high                          | ideas are never recorded              |
| sparks are not searchable                          | sparks become dead storage            |
| Scintilla demands premature judgment               | intake collapses before thought forms |
| spark bundles lose audio/transcript/json coherence | provenance becomes muddy              |

---

# Engine 2 — Respice Finem

## Role

Turn sparks into goals.

Finis is the purpose layer.
It should help the user move from raw sparks to defined ends.

## Primary Inputs

Live now:

```text
data/scintilla/sparks/
data/scintilla/transcripts/
manual user input
```

## Canonical Output Artifacts

Live canonical goal storage:

```text
data/finis/goals/
```

Typical canonical goal files:

```text
FINIS_001.md
FINIS_002.md
```

## Canonical Goal Record

A canonical goal record should support at least:

```text
goal_id
title
description
status
created
derived_from
```

Additional fields may exist, but goals should remain inspectable and diff-friendly.

## Live Commands

```text
azq fine
azq goals
azq goal add
azq goal close <goal_id>
azq goal archive <goal_id>
```

## Live Responsibilities

* read sparks and propose candidate goals through the current `azq fine` flow
* store accepted goals as canonical Markdown files
* list active goals
* allow manual goal creation
* allow explicit goal closure and archiving

## Future Direction

Finis is the first engine that must deepen significantly.

Future Finis behavior should remain **inside Finis** and should include:

* spark inspection
* clustering or weighing related sparks
* narrowing questions
* tractability notes
* usefulness notes tied to the current repository or effort
* refined goal proposals
* optional manifesto, intent, or vision-note support attached to goal work

Possible future proposal artifact homes inside Finis may include:

```text
data/finis/proposals/
data/finis/notes/
```

These are internal Finis homes, not a new public craft layer.

## Engine Boundary

Finis should shape **ends**, not deliverables and not task lists.

It may help write or refine purpose language, but it should stop before artifact architecture.
That boundary belongs to Formam.

## Failure Modes

| Failure                                               | Result                                                         |
| ----------------------------------------------------- | -------------------------------------------------------------- |
| spark overload                                        | noise accumulates without purpose                              |
| goals are vague                                       | later structural work becomes muddy                            |
| Finis stores goals but does not shape them            | the engine becomes a filing cabinet instead of a purpose layer |
| LLM proposals silently overwrite accepted goals       | trust collapses                                                |
| narrowing questions are hidden instead of inspectable | user judgment gets buried                                      |

---

# Engine 3 — Strue Formam

## Role

Turn goals into structural deliverables and maps.

Formam is the form layer.
It defines what should exist if a goal succeeds.

## Primary Inputs

```text
data/finis/goals/
repository context
accepted goal context
```

## Canonical Output Artifacts

```text
data/form/deliverables/
data/form/maps/
```

Typical files:

```text
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_FINIS_001_MAP.md
```

## Canonical Deliverable Record

A deliverable should support at least:

```text
deliverable_id
goal_id
title
artifact_description
dependencies
status
```

## Live Commands

```text
azq form build <goal_id>
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
```

## Live Responsibilities

* create the current first-form baseline for a goal
* write canonical deliverable records
* write or refresh goal maps
* allow deliverables to be listed and inspected

## Future Direction

Formam should deepen into an LLM-assisted deliverable-shaping layer.

Future Formam behavior should remain **inside Formam** and should include:

* deliverable generation
* deliverable expansion
* prioritization
* first-now versus later distinctions
* boundary clarification
* map refinement and dependency notes

Possible future proposal artifact homes inside Formam may include:

```text
data/form/proposals/
data/form/expansions/
```

These are Formam internals, not a new public engine.

## Engine Boundary

Formam should define **what should exist**, not explode immediately into executable tasks.

It should resist the urge to become a task manager.
That next shaping boundary belongs to Agenda.

## Failure Modes

| Failure                                     | Result                                              |
| ------------------------------------------- | --------------------------------------------------- |
| form stage is skipped                       | tasks become chaotic and decontextualized           |
| deliverables are vague                      | execution produces partial or incoherent artifacts  |
| Formam only writes one stub forever         | the engine never grows into real structural shaping |
| prioritization is absent                    | everything feels equally urgent                     |
| Formam starts decomposing into tasks itself | craft boundaries collapse                           |

---

# Engine 4 — Age Agenda

## Role

Turn deliverables into executable work.

Agenda is the action layer.
It should shape a deliverable into tasks, dependency order, execution context, and Codex-ready work.

## Primary Inputs

```text
data/form/deliverables/
data/form/maps/
accepted deliverable context
```

## Canonical Output Artifacts

```text
data/agenda/tasks/
data/agenda/dags/
data/agenda/logs/
```

Typical files:

```text
data/agenda/tasks/TASK_001.md
data/agenda/dags/GOAL_FINIS_001_DAG.json
data/agenda/logs/TASK_001_LOG.md
```

## Canonical Task Record

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

## Live Commands

```text
azq agenda build <deliverable_id>
azq agenda list
azq agenda show <task_id>
azq agenda dag <deliverable_id>
```

These are the current live Stage 3 commands.

The older broader split between `azq task ...` and `azq dag ...` is **not** the live baseline and should not be taught as current behavior unless later code explicitly adds those families.

## Live Responsibilities

* create current canonical task stubs for one deliverable
* list canonical tasks
* inspect one canonical task
* refresh a goal-level DAG artifact reached from one exact deliverable

## Future Direction

Agenda should deepen into the LLM-assisted task-and-Codex layer.

Future Agenda behavior should remain **inside Agenda** and should include:

* commit-sized task decomposition
* task proposal generation
* task deduplication
* deterministic dependency DAG generation
* execution levels or ordering support
* Codex preparation
* Codex execution reporting

Possible future proposal and execution artifact homes inside Agenda may include:

```text
data/agenda/proposals/
data/agenda/reports/
data/agenda/runs/
```

These remain Agenda-owned artifacts, not a new public engine.

## Engine Boundary

Agenda should shape **executable work**.
It is the correct home for task decomposition and Codex preparation.

Agenda should not become archive stewardship.
That belongs to Domum.

## Failure Modes

| Failure                                               | Result                                  |
| ----------------------------------------------------- | --------------------------------------- |
| tasks detach from deliverables                        | activity becomes meaningless            |
| no DAG or dependency visibility                       | execution order becomes guesswork       |
| generated tasks are too large                         | Codex handoff becomes sloppy            |
| dedupe is missing                                     | repeated work accumulates               |
| Codex preparation lives in stray side scripts forever | the real operator flow stays fragmented |

---

# Engine 5 — Custodi Domum

## Role

Steward the system.

Domum is the preservation and review layer.
It should protect evidence, reduce entropy, and later support repository-wide introspection.

## Primary Inputs

```text
accepted craft artifacts
archivable artifacts
completed work
stale or superseded material
```

## Future Canonical Output Artifacts

Domum is not live yet, but expected homes include:

```text
data/archive/
data/reports/
```

Likely archive families include:

```text
data/archive/sparks/
data/archive/goals/
data/archive/deliverables/
data/archive/tasks/
data/archive/artifacts/
```

## Live Commands

There is no live Domum command family yet.

## Future Direction

Domum should eventually own:

* archive
* prune
* review
* repository-wide stewardship
* later `status`
* later `doctor`

Reasonable future commands include:

```text
azq archive ...
azq prune
azq review
azq status
azq doctor
```

## Engine Boundary

Domum should arrive **after** archive paths exist and after the action layers are strong enough to preserve.

It should not be asked to create the missing planning intelligence of Finis, Formam, or Agenda.
Its job is stewardship and introspection.

## Failure Modes

| Failure                                                            | Result                                      |
| ------------------------------------------------------------------ | ------------------------------------------- |
| archive friction is too high                                       | clutter accumulates and users keep deleting |
| archive comes too late                                             | evidence is lost before stewardship exists  |
| review is absent                                                   | history becomes invisible                   |
| `status` and `doctor` arrive before the filesystem truth is stable | introspection becomes unreliable            |

---

# Global System Properties

## Inspectability

Intermediate artifacts must remain visible.
A user should be able to inspect goals, deliverables, tasks, DAGs, and later archives directly from disk.

## Plain Durable Formats

The system favors durable, diff-friendly formats such as:

```text
markdown
json
csv
```

## Reversible Thinking

The user should be able to revisit earlier stages.
The craft path is directional, but inspection should work backward:

```text
task -> deliverable -> goal
deliverable -> goal
goal -> spark or manual origin
```

## Human Judgment Remains Central

AZQ assists thought.
It does not replace judgment.

The user remains responsible for:

* deciding what matters
* rejecting weak proposals
* accepting or declining LLM-shaped artifacts
* determining what deserves to be built
* deciding when generated work is good enough to execute

---

# Live Baseline Summary

The current live baseline proven by bootstrap is:

* Scintilla can capture and inspect sparks
* Finis can store and list canonical goals
* Formam can create and inspect canonical deliverables and maps
* Agenda can create and inspect canonical task records and goal-level DAGs

That live path is:

```text
spark -> goal -> deliverable -> task -> dag
```

The next implementation work deepens the existing engines rather than adding new public ones:

* Finis gains real goal-shaping behavior
* Formam gains real deliverable-shaping behavior
* Agenda gains real task-shaping and Codex-preparation behavior
* Domum arrives afterward as stewardship and introspection

---

# Closing

The engines should mean what their names imply.

* **Scintilla** should gather sparks
* **Finis** should shape goals
* **Formam** should shape deliverables
* **Agenda** should shape executable work
* **Domum** should steward what remains

If implementation keeps those meanings intact, doctrine and code can converge.
If engine boundaries are ignored, AZQ will drift into a muddled task system with decorative Latin labels.

This specification exists to prevent that drift.
