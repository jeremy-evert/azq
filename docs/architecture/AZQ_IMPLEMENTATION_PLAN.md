# AZQ Implementation Plan

## Purpose

AZQ exists to help Jeremy work with LLMs without losing the thread of his own mind.

It is a file-backed cognitive wrapper for LLM-assisted work: a system for capturing sparks, shaping goals, defining deliverables, structuring executable tasks, and preserving lineage across repeated interactions with language models.

AZQ is not merely a planner, not merely a task manager, and not merely a CLI over some Markdown files.

AZQ exists to do five things well:

1. preserve human intent before an LLM reshapes it
2. turn fleeting thought into durable artifacts
3. maintain lineage from spark to execution
4. create work packages that can be handed to LLMs without losing the original purpose
5. make LLM-assisted work inspectable, resumable, and reviewable over time

This document defines the implementation plan for AZQ as it exists now.

It is not a speculative roadmap for a repository that has not yet been built.
It is a rebased implementation plan that starts from the current repository truth, names the implemented baseline, identifies what remains partial, and defines the real forward work that belongs next.

This plan must stay truthful about three different things:

1. the implemented baseline in code
2. the checked-in artifact snapshot under `data/`
3. the forward implementation scope that remains after the current baseline

This plan should therefore be read as both:

- a truthful architectural description of the current AZQ baseline
- a practical source document for later deliverable extraction

---

## Core Mission

AZQ is a human-first wrapper around LLM collaboration.

Its job is not to replace judgment.
Its job is not to let the model drive the bus into a lake with excellent confidence.
Its job is to help the human remain oriented.

AZQ should preserve:

- what the human originally meant
- what was captured
- what was promoted into a goal
- what was shaped into a deliverable
- what became executable work
- what was handed to an LLM
- what came back
- what should happen next

That means every engine in AZQ exists in relation to LLM-assisted work:

- **Scintilla** preserves raw thought before it is diluted or forgotten
- **Finis** stabilizes intent before an LLM reframes the objective
- **Formam** defines the artifact boundaries an LLM can actually work on
- **Agenda** shapes executable work and eventual model handoff
- later stewardship layers preserve continuity across repeated sessions, revisions, and generated outputs

If AZQ ever forgets this mission, it collapses into a dressed-up task manager.
That is not the point of the system.

---

## Planning Posture

This implementation plan follows four rules:

### 1. Match the repository on disk

Code, tests, and checked-in planning artifacts are stronger evidence than stale prose.

### 2. Preserve the distinction between baseline and aspiration

Implemented baseline work should not be re-described as though it were still pending.
Partial areas should be named plainly instead of being inflated into "done."

### 3. Keep the system mission visible

The point of AZQ is not generic planning.
The point is structured continuity of mind while working with LLMs.

### 4. Decompose only genuine pending work later

Later deliverable extraction should target real incomplete areas, not the already-implemented Stage 1 through Stage 3 baseline.

---

## Current Repository Baseline

The current repository already implements the first four live craft families under `azq/`:

- `scintilla`
- `finis`
- `formam`
- `agenda`

The live CLI surface currently includes:

- `azq capture`
- `azq sparks`
- `azq spark <id>`
- `azq spark search <text>`
- `azq spark rm <id>`
- `azq fine`
- `azq goals`
- `azq goal add`
- `azq goal close <id>`
- `azq goal archive <id>`
- `azq form build <goal_id>`
- `azq form list`
- `azq form show <deliverable_id>`
- `azq form map <goal_id>`
- `azq agenda build <deliverable_id>`
- `azq agenda list`
- `azq agenda show <task_id>`
- `azq agenda dag <deliverable_id>`

That means the repository already supports the visible craft path:

```text
spark -> goal -> deliverable -> task -> dag
````

This baseline is supported by:

* the live code under `azq/`
* the stage planning tree under `planning/stage_1/`, `planning/stage_2/`, and `planning/stage_3/`
* the regression suites under `tests/`
* the current Codex planning and status artifacts under `codex/reports/`

This plan therefore treats Stage 1 through Stage 3 as the implemented baseline architecture, not as pending roadmap work.

### Code capability versus checked-in data snapshot

The repository code is Stage 3-capable.

The checked-in `data/` tree is narrower than the code capability.

Current checked-in data reality:

| Area                | Checked-in state                                          |
| ------------------- | --------------------------------------------------------- |
| `data/scintilla/`   | populated with audio, transcripts, and spark JSON         |
| `data/finis/goals/` | populated with canonical goal files                       |
| `data/form/`        | directories exist, but no checked-in deliverables or maps |
| `data/agenda/`      | directories exist, but no checked-in tasks, DAGs, or logs |

This distinction matters.

The repository can truthfully claim:

* a Stage 3-capable code baseline
* live Scintilla and Finis artifact families in checked-in data

The repository should not overstate:

* a fully populated checked-in Stage 2 artifact snapshot
* a fully populated checked-in Stage 3 artifact snapshot
* a fully deepened LLM handoff layer

---

## AZQ As A Cognitive Wrapper

AZQ should be understood as a layered wrapper around LLM-assisted work.

### Scintilla protects the spark

Scintilla captures thought before it evaporates.
It stores the raw material of intention in a form that can later be reviewed, promoted, or discarded.

### Finis protects the end

Finis helps answer:
"What am I actually trying to do?"

That matters because LLMs are very good at producing plausible means before the human has stated the end clearly.

### Formam protects the shape

Formam helps answer:
"If this goal succeeds, what must exist in the world?"

That matters because LLMs work better when asked to produce bounded artifacts rather than vague ambition soup.

### Agenda protects the handoff

Agenda helps answer:
"What work package should be executed next, and how should that work be structured so an LLM can help without derailing the mission?"

That is where Codex, or another model, eventually becomes a useful collaborator instead of a glitter cannon.

### Stewardship protects continuity

Future archive, Domum, status, and doctor surfaces should help answer:

* what happened
* what exists
* what drifted
* what needs repair
* what should be resumed
* what should be retired

That is how AZQ stops each LLM session from becoming a goldfish bowl.

---

## Implemented Baseline By Stage

## Scintilla Intake Baseline

### What exists now

Scintilla is the live intake layer.

It currently owns:

* audio capture
* transcript writing
* spark extraction
* spark listing
* exact-id spark inspection
* spark search
* destructive spark deletion

Canonical Scintilla storage is:

* `data/scintilla/audio/`
* `data/scintilla/transcripts/`
* `data/scintilla/sparks/`

### Why it exists in the larger mission

Scintilla exists to preserve raw thought before LLM collaboration begins in earnest.

It is the "do not lose the signal" layer.

Without it, work starts after memory has already blurred, and the LLM is invited to improvise over missing context.

### What is still limited

Scintilla is live but still partial:

* no text-native capture path exists
* no archive-first spark retirement exists
* deletion is still destructive
* transcription still carries import-time operational weight
* there is no richer review loop around captured sparks

Scintilla should therefore be treated as **implemented intake baseline, not fully deepened capture stewardship**.

---

## Stage 1: Finis Baseline

### What exists now

The Finis baseline is implemented under `azq/finis/`.

Canonical goal storage exists under:

```text
data/finis/goals/
```

Legacy migration input remains present at:

```text
data/finis/goals.json
```

### What behavior is supported now

The current Finis baseline supports:

* canonical one-goal-per-file Markdown storage
* stable `FINIS_###` goal ids
* deterministic goal lookup and listing
* manual goal creation
* goal close and goal archive status updates
* migration from legacy `goals.json`
* simple spark-to-goal promotion through `azq fine`

The current `azq fine` flow is real but intentionally light:

* it reads spark JSON
* it cleans candidate titles
* it dedupes against existing goals
* it asks for confirmation
* it writes accepted canonical goal files

### Why it exists in the larger mission

Finis exists to stabilize human intent before the system asks an LLM to help.

Its role is not merely to store goals.
Its role is to keep the human from accidentally outsourcing the question of purpose.

Finis should help the human say:

* what matters
* what success looks like
* what problem is actually being solved
* what not to chase

That makes later LLM interaction safer and more useful.

### What storage and forms are canonical now

Canonical Stage 1 storage is:

* goal files named `FINIS_###.md` under `data/finis/goals/`

Canonical goal record fields in practice are:

* `goal_id`
* `title`
* `status`
* `created`
* `description`
* `derived_from`

### What supports this baseline

Strong supporting evidence includes:

* `planning/stage_1/overview.md`
* `planning/stage_1/wave_a/tasks.json`
* `planning/stage_1/wave_b/tasks.json`
* `planning/stage_1/wave_c/tasks.json`
* `tests/test_stage1_wave_c.py`
* `codex/reports/codex_azq_task_status_report.md`

### What is still limited within Stage 1

The Finis baseline is implemented, but deeper goal shaping does not yet exist:

* no proposal artifacts
* no narrowing-question flow
* no tractability notes
* no usefulness analysis
* no explicit LLM-facing goal preparation flow
* no richer review loop that distinguishes "good candidate goal" from "interesting spark"

Stage 1 should therefore be treated as **implemented baseline, partially deepened**.

---

## Stage 2: Formam Baseline

### What exists now

The Formam baseline is implemented under `azq/formam/`.

Canonical Formam storage homes exist under:

```text
data/form/deliverables/
data/form/maps/
```

### What behavior is supported now

The current Formam baseline supports:

* exact validation of canonical Finis parent goals before writes
* canonical one-deliverable-per-file Markdown storage
* canonical one-goal-map-per-goal Markdown storage
* deterministic `DELIV_###` id allocation
* `azq form build <goal_id>`
* `azq form list`
* `azq form show <deliverable_id>`
* `azq form map <goal_id>`

`azq form build <goal_id>` currently creates:

* one deterministic stub deliverable
* one goal map artifact for that goal

That is real behavior, not future roadmap language.

### Why it exists in the larger mission

Formam exists to turn intent into shape.

Its role is to identify the artifacts, components, or outputs that must exist if a goal succeeds.

This is where AZQ moves from "what do I want?" to "what should exist so that an LLM can help build it without guessing the structure from fumes."

Formam protects the project from vague-goal syndrome.

It makes later work package generation possible.

### What storage and forms are canonical now

Canonical Stage 2 storage is:

* deliverable files named `DELIV_###.md` under `data/form/deliverables/`
* goal map files named like `GOAL_<goal_id>_MAP.md` under `data/form/maps/`

Canonical deliverable fields in practice are:

* `deliverable_id`
* `goal_id`
* `title`
* `artifact_description`
* `dependencies`
* `status`
* `created`

Canonical goal-map fields in practice are:

* `goal_id`
* `deliverable_ids`
* `dependency_edges`
* `status`
* `created`
* `notes`

### What supports this baseline

Strong supporting evidence includes:

* `planning/stage_2/overview.md`
* `planning/stage_2/wave_a/tasks.json`
* `planning/stage_2/wave_b/tasks.json`
* `planning/stage_2/wave_c/tasks.json`
* `planning/stage_2/wave_d/tasks.json`
* `tests/test_stage2_wave_c.py`
* `codex/reports/codex_azq_task_status_report.md`

### What is still limited within Stage 2

The Formam baseline is implemented, but still intentionally narrow:

* deliverable generation is stub-first
* goal maps remain sparse
* there is no proposal/acceptance path for expanded deliverables
* there is no prioritization layer
* there is no explicit LLM-assisted deliverable shaping
* compatibility support for older naming still exists in storage code

Stage 2 should therefore be treated as **implemented baseline, partially deepened**.

---

## Stage 3: Agenda Baseline

### What exists now

The Agenda baseline is implemented under `azq/agenda/`.

Canonical Agenda storage homes exist under:

```text
data/agenda/tasks/
data/agenda/dags/
data/agenda/logs/
```

### What behavior is supported now

The current Agenda baseline supports:

* exact validation of canonical Formam deliverables before task writes
* canonical one-task-per-file Markdown storage
* canonical goal-level DAG JSON artifacts
* canonical task-log helper storage
* deterministic `TASK_###` id allocation
* shared exact task ancestry resolution through deliverable lineage
* `azq agenda build <deliverable_id>`
* `azq agenda list`
* `azq agenda show <task_id>`
* `azq agenda dag <deliverable_id>`

`azq agenda build <deliverable_id>` currently creates:

* one deterministic stub task for that deliverable

`azq agenda dag <deliverable_id>` currently creates or refreshes:

* one goal-level DAG artifact reached through that deliverable’s parent goal

### Why it exists in the larger mission

Agenda exists to shape executable work for human review and eventual LLM assistance.

It is the layer that should eventually answer:

* what is the next coherent work package
* what depends on what
* what is small enough for a sane commit
* what can be handed to Codex or another model without losing the intent lineage

Agenda is not just a task list.
It is the execution-handoff layer for LLM-assisted work.

### What storage and forms are canonical now

Canonical Stage 3 storage is:

* task files named `TASK_###.md` under `data/agenda/tasks/`
* goal-level DAG files named like `GOAL_<goal_id>_DAG.json` under `data/agenda/dags/`
* task-log files named like `<task_id>_LOG.md` under `data/agenda/logs/`

Canonical task fields in practice are:

* `task_id`
* `deliverable_id`
* `title`
* `status`
* `task_intent`
* `description`
* `dependencies`
* `execution_notes`
* `created`

Canonical DAG fields in practice are:

* `graph_id`
* `goal_id`
* `deliverable_ids`
* `task_ids`
* `dependency_edges`
* `status`
* `created`
* `notes`

### What supports this baseline

Strong supporting evidence includes:

* `planning/stage_3/overview.md`
* `planning/stage_3/wave_a/tasks.json`
* `planning/stage_3/wave_b/tasks.json`
* `planning/stage_3/wave_c/tasks.json`
* `planning/stage_3/wave_d/tasks.json`
* `tests/test_stage3_wave_c.py`
* `tests/test_stage3_wave_d.py`
* `codex/reports/codex_azq_task_status_report.md`

### What is still limited within Stage 3

The Agenda baseline is implemented, but still materially limited:

* `agenda build` creates stub tasks rather than commit-sized decompositions
* task dedupe does not exist
* Codex preparation and execution reporting do not exist
* task logs exist as storage helpers, but are not part of the live build flow
* the CLI does not yet expose richer lifecycle mutation commands
* there is no explicit model-facing packaging layer yet

Stage 3 should therefore be treated as **implemented baseline, partially deepened**.

---

## Current Engine State By Subsystem

## Scintilla

### Current live state

Scintilla is the live spark intake layer.

It currently owns:

* audio capture
* transcript writing
* spark extraction
* spark listing
* exact-id spark inspection
* spark search
* destructive spark deletion

Current structural boundary:

* Scintilla gathers and exposes spark bundles
* it does not shape goals, deliverables, or tasks

### Current mission fit

Scintilla already does real work for the LLM-wrapper mission because it preserves source thought before it gets blurred by later conversation.

### Current limits

Scintilla is still partial because:

* no text-native capture path exists
* no archive-first retirement exists
* deletion is still destructive
* richer spark triage does not exist

---

## Finis

### Current live state

Finis is the live goal layer.

It currently owns:

* canonical goal storage
* exact goal lookup and listing
* manual goal creation
* goal status updates
* simple spark-to-goal promotion through `azq fine`

Current structural boundary:

* Finis shapes ends
* it does not define deliverables or decompose work into tasks

### Current mission fit

Finis is the first serious protection against LLM drift.
It keeps the project grounded in human intention.

### Current limits

Finis is still partial because:

* shaping is candidate-promotion rather than proposal-rich analysis
* there are no canonical proposal homes
* there is no question flow or review flow
* there is no stronger LLM-facing intent packaging

---

## Formam

### Current live state

Formam is the live structure layer.

It currently owns:

* canonical deliverable storage
* canonical goal-map storage
* parent-goal validation
* build/list/show/map CLI behavior

Current structural boundary:

* Formam defines artifact boundaries and maps
* it does not own task decomposition or execution packaging

### Current mission fit

Formam is where AZQ becomes legible to an LLM.
It defines the shape of what should exist instead of throwing a model into a fog bank with a flashlight and a prayer.

### Current limits

Formam is still partial because:

* deliverable generation is stub-first
* map generation remains conservative
* no expansion, prioritization, or proposal flows exist

---

## Agenda

### Current live state

Agenda is the live executable-work layer.

It currently owns:

* canonical task storage
* canonical DAG storage
* canonical task-log helpers
* task-to-deliverable-to-goal lineage resolution
* build/list/show/dag CLI behavior

Current structural boundary:

* Agenda shapes executable work from deliverables
* it does not yet own artifact publication or repository stewardship

### Current mission fit

Agenda is the layer most directly pointed at Codex and similar tools, even if the full handoff flow is not yet built.

### Current limits

Agenda is still partial because:

* decomposition is stub-first
* dedupe does not exist
* Codex preparation does not exist
* task logs are not integrated into live build behavior
* execution reporting does not exist

---

## What Is Only Partially Complete

The following areas are real and implemented, but still materially incomplete:

| Area                        | Current truth                                              | Why it remains partial                                                 |
| --------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------- |
| Scintilla retirement        | `azq spark rm <id>` is still live                          | archive-first behavior has not replaced destructive deletion           |
| Scintilla capture           | audio path is live                                         | no text-native capture path or richer review loop                      |
| Finis shaping               | `azq fine` promotes goals interactively                    | no proposal files, narrowing questions, or deeper analysis             |
| Formam shaping              | `azq form build` creates stub deliverables and sparse maps | no expansion, prioritization, or proposal acceptance flow              |
| Agenda shaping              | `azq agenda build` creates stub tasks                      | no task decomposition, dedupe, Codex preparation, or execution reports |
| Agenda logs                 | task-log storage helpers exist                             | build flow and CLI do not yet make logs part of normal execution       |
| Repository-wide stewardship | architecture points toward Domum, status, and doctor       | none of those surfaces are live                                        |

These partial areas are the correct future decomposition targets.

---

## Known Repo And Documentation Mismatches

The current repository still contains a few important mismatches.

### 1. The implementation plan was previously stale

Earlier forms of this document described Stage 1 through Stage 3 as future roadmap work.
That no longer matches the code, planning tree, or tests.

### 2. Some architecture prose still lags live repo truth

The state model still includes command or storage assumptions that are not current live behavior.

Examples include:

* older reliance on `data/finis/goals.json`
* non-live command examples
* archive/prune behavior that is not implemented

Where code and tests disagree with older prose, code and tests are stronger evidence.

### 3. `pyproject.toml` lags the real baseline

Repository metadata still describes AZQ as beginning with Scintilla.
That understates the current Stage 3-capable codebase.

### 4. Code capability exceeds checked-in artifact population

The code can produce Stage 2 and Stage 3 artifacts.
The checked-in `data/` tree does not currently demonstrate that full artifact population.

### 5. Some checked-in data is imperfect

At least one Finis backlink is inconsistent with current Scintilla artifact presence.
This is a data-quality issue, not proof that the Stage 1 baseline is absent.

---

## Forward Implementation Scope

The forward implementation scope begins **after** the current Stage 1 through Stage 3 baseline.

It should focus only on genuine pending work.
It should not reopen completed baseline storage, routing, or stage-introduction work as though those layers were still absent.

The forward scope is:

1. deepen Finis into a stronger human-intent shaping layer
2. deepen Formam into a stronger artifact-shaping layer for LLM collaboration
3. deepen Agenda into a task-decomposition, dedupe, and model-handoff layer
4. replace destructive retirement paths with safer archive-first behavior
5. implement Domum and later repository-wide stewardship surfaces
6. add repository-wide readers such as `status` and `doctor`

This order is deliberate.

The current repository already has the baseline craft sequence.
The next work should deepen the existing engines so they actually serve the LLM-wrapper mission more completely.

### Genuine pending work only

Pending work includes:

* deeper shaping
* proposal artifacts
* LLM-facing preparation layers
* safer archive behavior
* stewardship and repository readers

Pending work does **not** include:

* re-introducing canonical goal storage
* re-introducing Formam
* re-introducing Agenda
* re-splitting the CLI into engine routers

Those are already baseline reality.

---

## Proposed Next Stages After The Current Baseline

## Stage 4: Deepen Finis As The Human-Intent Layer

### Objective

Turn Finis from simple candidate promotion into a visible goal-shaping layer with proposal artifacts, narrowing questions, and judgment aids.

### Why it matters

This is where AZQ should help the human clarify purpose before the LLM starts offering means.

### Likely scope

* proposal artifacts under `data/finis/`
* narrowing-question support
* tractability and usefulness notes
* richer spark inspection flows
* explicit review states before a goal becomes canonical
* better packaging of human intent for later model-facing steps

This stage should deepen existing canonical goals rather than replace them.

---

## Stage 5: Deepen Formam As The Artifact-Shaping Layer

### Objective

Turn Formam from stub deliverable generation into a visible deliverable-shaping layer with refinement, expansion, and prioritization.

### Why it matters

LLMs do better with bounded artifacts than with vague ambition.
Formam is where the work becomes shapeable.

### Likely scope

* deliverable proposals or expansions
* prioritization
* "build now" versus "later" distinctions
* richer map refinement
* better artifact descriptions for downstream LLM use

This stage should preserve Formam’s boundary: define what should exist, not executable task lists.

---

## Stage 6: Deepen Agenda As The Model-Handoff Layer

### Objective

Turn Agenda from stub task generation into a visible task-shaping and model-handoff layer.

### Why it matters

This is the place where AZQ should start producing work packages that can safely be handed to Codex or another LLM backend.

### Likely scope

* commit-sized task decomposition
* task dedupe
* deterministic dependency refinement
* Codex preparation subsets
* execution reports
* stronger task-log integration
* possible backend-neutral packaging for multiple LLMs

This stage should stay inside Agenda rather than inventing a separate execution engine too early.

---

## Stage 7: Archive-First Stewardship And Domum

### Objective

Make stewardship real by introducing archive homes, replacing destructive retirement paths where appropriate, and adding the Domum engine.

### Why it matters

AZQ cannot be a continuity system if retirement is still a trap door and repository memory is a loose handful of scraps.

### Likely scope

* archive home under `data/`
* archive commands and archive markers or moves
* live `domum` package
* visible review and maintenance artifacts
* safer retirement of sparks and later artifacts

This stage should begin with safe archive paths before broader pruning or cleanup policy.

---

## Stage 8: Repository-Wide Readers

### Objective

Add `status` and `doctor` style repository readers once stewardship exists.

### Why it matters

The human should be able to ask the system:

* what state am I in
* what is missing
* what is stale
* what drifted
* what should I look at next

### Likely scope

* repository maturity classification from visible files
* repository health warnings from visible contradictions
* explicit reports instead of hidden orchestration
* reader surfaces that summarize continuity across LLM-assisted work

These readers should report what is visibly true on disk.

---

## Planning Guidance For Later Deliverable Decomposition

Later deliverables should be extracted from this plan using the following rules.

### 1. Decompose only genuine pending work

Do not re-decompose:

* Stage 1 Finis baseline introduction
* Stage 2 Formam baseline introduction
* Stage 3 Agenda baseline introduction

Those are already implemented baseline work.

### 2. Extract deliverables as repo-grounded artifacts or behaviors

Good later deliverables are things like:

* a visible Finis proposal flow
* a Formam deliverable expansion path
* an Agenda task dedupe flow
* a model-handoff packaging flow
* archive-first spark retirement
* a Domum archive reader
* a `status` report grounded in visible repository maturity

Deliverables should point to concrete behaviors, concrete artifact homes, or concrete command surfaces.

### 3. Use partial areas as the real decomposition targets

The correct later targets are:

* deeper Finis shaping
* deeper Formam shaping
* deeper Agenda shaping
* LLM-facing handoff packaging
* archive-first replacement of destructive paths
* Domum
* `status`
* `doctor`

### 4. Keep code capability and checked-in data separate

If a deliverable is about runtime capability, validate it against code and tests.
If it is about artifact truth on disk, validate it against checked-in or newly generated artifacts.

### 5. Prefer engine-owned decomposition

Future deliverables should stay within the existing engines:

* Finis-owned goal shaping
* Formam-owned artifact shaping
* Agenda-owned task shaping and model handoff
* Domum-owned stewardship and repository readers

This keeps the architecture coherent and avoids unnecessary engine explosion.

### 6. Preserve the mission in every decomposition pass

Every future deliverable should be checked against one question:

> Does this help the human keep hold of intent, lineage, and continuity while working with LLMs?

If the answer is no, it may still be nice plumbing, but it is not core AZQ work.

---

## Notes On Checked-In Data Versus Code Capability

The repository currently mixes strong code capability with a narrower checked-in artifact snapshot.

That should be interpreted carefully:

* Scintilla and Finis are demonstrated both by code and by committed artifacts
* Formam and Agenda are demonstrated strongly by code, planning, and tests
* Formam and Agenda are **not** demonstrated by committed artifact examples in the current `data/` tree

There is one further nuance:

* Agenda task-log storage exists as code capability
* task-log creation is not yet part of the normal `agenda build` baseline

So the repository can truthfully claim:

* Stage 3-capable code baseline
* a live chain from spark through DAG in code and tests
* a real mission-directed architecture for later LLM collaboration

The repository should not overstate:

* a fully populated checked-in Stage 3 artifact snapshot
* a fully deepened model handoff layer
* a fully realized stewardship layer

---

## Conclusion

AZQ already has an implemented baseline:

```text
spark -> goal -> deliverable -> task -> dag
```

But that chain is not the whole point.

The point of AZQ is to help Jeremy work with LLMs without losing orientation, lineage, or purpose.

The implemented baseline matters because it gives the system real structure.
The forward work matters because that structure still needs to become a better cognitive wrapper and a better model-handoff system.

What remains partial is not the existence of Scintilla, Finis, Formam, or Agenda.
What remains partial is the deeper shaping behavior, safer stewardship, and stronger LLM-facing continuity that the architecture is meant to support.

The correct next planning move is therefore:

* keep the implemented baseline intact
* deepen the engines where they are still thin
* preserve the system’s mission in every later decomposition pass
* extract future deliverables only from the still-partial post-baseline work

### Closing summary

This implementation plan is grounded in:

* the live code under `azq/`
* the stage planning artifacts under `planning/`
* the regression suites under `tests/`
* the checked-in artifact homes under `data/`
* the current Codex gap analysis and rebased-plan work

The baseline already complete is:

* live Scintilla intake
* Stage 1 Finis baseline
* Stage 2 Formam baseline
* Stage 3 Agenda baseline

What remains partial is:

* deeper Finis shaping
* deeper Formam shaping
* deeper Agenda shaping
* explicit model-handoff packaging
* archive-first behavior
* Domum
* repository-wide `status` and `doctor`

What should be decomposed later into stage deliverables is the post-baseline work above, not the already-implemented baseline.
