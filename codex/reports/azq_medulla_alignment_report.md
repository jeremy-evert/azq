# AZQ Medulla Alignment Report

## Executive Summary

This report audits the architecture-document layer against `docs/architecture/AZQ_Medulla.md`, using the live repository as source of truth.

The strongest conclusion is simple: the repo still carries the marrow of AZQ, but the architecture layer is not uniformly safe to treat as one flat authority set.

The strongest servants of the Medulla are `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md`, `docs/architecture/AZQ_ENGINE_SPEC.md`, `docs/architecture/AZQ_COMMAND_MODEL.md`, `docs/architecture/AZQ_FILESYSTEM_MODEL.md`, `docs/architecture/AZQ_BOOTSTRAP.md`, and `README.md`. Those documents usually preserve human-first purpose, lineage, canonical file-backed truth, and the warning that AZQ must not collapse into a generic task manager.

The main risks come from `docs/architecture/AZQ_STATE_MODEL.md`, `docs/architecture/AZQ_CRAFT_CHARTER.md`, `docs/architecture/AZQ_PLANNING_LOOP.md`, and secondarily `docs/architecture/AZQ_Manifesto.md`. The state model is the most build-risky document because it still teaches non-live commands, stale Finis storage claims, and state transitions that the repo does not currently protect. The craft charter is sound in structure but weak in marrow where it treats deletion and pruning too casually relative to Medulla's continuity standard. The planning loop is spiritually sympathetic, but it can pull future work toward a generic visible-planning system unless it is explicitly subordinated to the craft engines and accepted-state rules.

Judgment on safety: the current architecture-document layer is not strong enough to let future Opifex / Codex work proceed safely if all documents are treated as equal authority. It is safe enough only if work is explicitly governed by `AZQ_Medulla.md`, checked against the live code under `azq/`, and then read through the implementation, engine, command, filesystem, and bootstrap documents in that order.

Some judgments below are conservative because the repo does not yet have live proposal artifact families under `data/finis/`, `data/form/`, or `data/agenda/`. Where a document describes those areas, this report treats doctrinal intent separately from current implementation truth.

## AZQ_Medulla Core Tests

Derived from `docs/architecture/AZQ_Medulla.md`:

- Preserves human intent rather than letting model output silently replace it.
- Preserves lineage from spark to goal to deliverable to task and later stewardship artifacts.
- Preserves continuity so a later human can still inspect what was captured, proposed, accepted, changed, and resumed.
- Distinguishes human-origin intent, model-origin suggestion, and accepted canonical state.
- Supports movement from spark to action through durable file-backed craft stages.
- Keeps AZQ human-first while still allowing LLM assistance.
- Resists drift into a generic task manager, generic planner, or loose helper-script pile.
- Resists destructive state changes that erase continuity without stewardship.

## Documents Inspected

Architecture and doctrine:

- `docs/architecture/AZQ_Medulla.md`
- `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md`
- `docs/architecture/AZQ_ENGINE_SPEC.md`
- `docs/architecture/AZQ_COMMAND_MODEL.md`
- `docs/architecture/AZQ_STATE_MODEL.md`
- `docs/architecture/AZQ_FILESYSTEM_MODEL.md`
- `docs/architecture/AZQ_CRAFT_CHARTER.md`
- `docs/architecture/AZQ_BOOTSTRAP.md`
- `docs/architecture/AZQ_Manifesto.md`
- `docs/architecture/AZQ_PHILOSOPHY.md`
- `docs/architecture/AZQ_PLANNING_LOOP.md`

Repo grounding:

- `README.md`
- `pyproject.toml`
- `azq/cli.py`
- `azq/scintilla/storage.py`
- `azq/scintilla/spark_delete.py`
- `azq/finis/storage.py`
- `azq/finis/fine.py`
- `azq/formam/build.py`
- `azq/formam/deliverable_storage.py`
- `azq/formam/map_storage.py`
- `azq/agenda/build.py`
- `azq/agenda/lineage.py`
- `azq/agenda/task_storage.py`
- `azq/agenda/dag_storage.py`
- `azq/agenda/log_storage.py`
- `planning/stage_1/overview.md`
- `planning/stage_2/overview.md`
- `planning/stage_3/overview.md`
- `tests/test_stage1_wave_c.py`
- `tests/test_stage2_wave_c.py`
- `tests/test_stage3_wave_c.py`
- `tests/test_stage3_wave_d.py`
- `data/finis/goals/FINIS_001.md`
- `data/finis/goals/FINIS_027.md`
- `data/scintilla/sparks/2026-03-09_090255.json`

## Medulla Alignment Matrix

| document | role | alignment status | Medulla strengths | Medulla risks | repo grounding | notes |
| --- | --- | --- | --- | --- | --- | --- |
| `docs/architecture/AZQ_Medulla.md` | doctrinal standard | strongly aligned | States the core sentence and non-negotiables plainly. Protects intent, lineage, continuity, accepted-vs-proposal distinction, and anti-task-manager drift. | None found inside the document. | `docs/architecture/AZQ_Medulla.md` | This is the governing standard, not just another architecture note. |
| `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md` | repo-truth architecture baseline | strongly aligned | Best balance of doctrine and live repo truth. Separates implemented baseline from future deepening. Repeats human-first LLM wrapper framing. | Slightly stronger than repo truth on Agenda logs as part of baseline. | `azq/cli.py`, `azq/finis/storage.py`, `azq/formam/build.py`, `azq/agenda/build.py`, `azq/agenda/log_storage.py`, `planning/stage_1/overview.md`, `planning/stage_2/overview.md`, `planning/stage_3/overview.md` | Strong marrow and strong build utility. |
| `docs/architecture/AZQ_ENGINE_SPEC.md` | engine boundaries and responsibilities | strongly aligned | Protects engine boundaries, proposal-vs-canonical distinction, archive-first direction, and anti-generic-planner drift. | Like the implementation plan, it names `data/agenda/logs/` as canonical output more strongly than the live build flow does. | `azq/scintilla/storage.py`, `azq/finis/storage.py`, `azq/formam/deliverable_storage.py`, `azq/formam/map_storage.py`, `azq/agenda/lineage.py`, `azq/agenda/log_storage.py` | One of the clearest servants of the Medulla. |
| `docs/architecture/AZQ_COMMAND_MODEL.md` | public CLI doctrine | strongly aligned | Keeps the craft sequence visible, keeps future intelligence inside existing engines, and clearly marks live vs future commands in most places. | Future command examples are fine, but could be misread if later copied without the live/future boundary. | `azq/cli.py`, `azq/scintilla/cli.py`, `azq/finis/cli.py`, `azq/formam/cli.py`, `azq/agenda/cli.py` | Good operator-facing doctrine. |
| `docs/architecture/AZQ_FILESYSTEM_MODEL.md` | on-disk truth and artifact boundaries | strongly aligned | Best document for canonical-vs-proposal separation. Strong on engine-owned artifact homes and anti-hidden-state posture. | Future proposal trees are only aspirational today. | `data/`, `azq/finis/storage.py`, `azq/formam/deliverable_storage.py`, `azq/formam/map_storage.py`, `azq/agenda/task_storage.py`, `azq/agenda/dag_storage.py` | Sound in marrow and highly build-relevant. |
| `docs/architecture/AZQ_BOOTSTRAP.md` | smallest proof-of-life path | strongly aligned | Truthful about the current live baseline and narrow enough to stay honest. Reinforces file-backed proof over rhetoric. | Overstates task logs slightly by listing them among canonical records even though bootstrap does not produce them. | `README.md`, `azq/cli.py`, `azq/formam/build.py`, `azq/agenda/build.py`, `azq/agenda/log_storage.py` | Strong because it stays small. |
| `README.md` | operator-facing orientation | strongly aligned | Names the live path, names what is not live, warns that `spark rm` is temporary, and preserves the anti-task-manager frame. | Says `azq/agenda/` builds task logs under `data/agenda/`, which is only partly true in current flow. | `azq/cli.py`, `azq/agenda/build.py`, `azq/agenda/log_storage.py`, `data/` | Strong live orientation document. |
| `docs/architecture/AZQ_PHILOSOPHY.md` | mission and design philosophy | partially aligned | Explicitly protects acceptance boundaries and warns against multiplying engines. Keeps the human in judgment. | Less grounded in live repo behavior. Useful doctrine, but not strong enough alone for build decisions. | `docs/architecture/AZQ_Medulla.md`, `azq/` baseline, `data/` layout | Better than the manifesto because it names proposal-vs-accepted craft. |
| `docs/architecture/AZQ_CRAFT_CHARTER.md` | high-level craft laws | partially aligned | Protects stages, artifacts-over-abstractions, deliverables-before-tasks, and human judgment. | `Law 4 — Deletion Is First-Class` sits badly against Medulla's continuity and archive-first standard. It does not clearly protect accepted-vs-proposal state or human-vs-model contribution. | `docs/architecture/AZQ_Medulla.md`, `azq/scintilla/spark_delete.py`, `README.md` | Structurally sound, but weak in marrow at key pressure points. |
| `docs/architecture/AZQ_PLANNING_LOOP.md` | visible reasoning doctrine | partially aligned | Strong on visible intermediate artifacts, human authorship, and inspectability. | Can flatten AZQ into a generic planning-artifact machine. It is not anchored tightly enough to spark-goal-deliverable-task lineage or accepted canonical state. | `docs/architecture/AZQ_Medulla.md`, `azq/`, `planning/`, absence of proposal stores in `data/` | Spiritually sympathetic, but off-center enough to require repair. |
| `docs/architecture/AZQ_Manifesto.md` | broad project ethos | stale but aligned | Strong anti-task-manager language and strong human-first craft framing. | Weak on lineage, continuity mechanics, accepted-vs-proposal state, and live repo grounding. More poetic than build-safe. | `docs/architecture/AZQ_Medulla.md`, `README.md`, `azq/` | Not anti-Medulla, but not protective enough for implementation work. |
| `docs/architecture/AZQ_STATE_MODEL.md` | formal lifecycle and command states | misaligned | Tries to make craft states explicit and does preserve some proposed/active distinctions in theory. | Most dangerous doc in the set. Teaches stale commands, stale Finis storage, non-live states, and transitions that the repo does not currently enforce. This weakens continuity because builders could implement against the wrong canonical truth. | `azq/cli.py`, `azq/finis/storage.py`, `azq/agenda/build.py`, `azq/agenda/log_storage.py`, `tests/test_stage1_wave_c.py`, `tests/test_stage3_wave_c.py` | Sound in structure, weak in marrow and unsafe in current form. |
| `pyproject.toml` | package metadata | stale but aligned | Not contradictory in doctrine. | The description still frames AZQ as “starting with Cole Scintilla,” which lags the Stage 3 baseline and weakens continuity between code and public identity. | `pyproject.toml`, `README.md`, `azq/` | Low doctrinal risk, clear staleness. |

## Strongly Aligned Documents

### `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md`

This is the strongest doctrine-to-repo bridge in the repo. It preserves the Medulla's human-first sentence, keeps AZQ centered as an LLM wrapper rather than a generic planner, and repeatedly distinguishes current implementation from future deepening. It also matches the live baseline under `azq/`, the populated `data/scintilla/` and `data/finis/`, and the Stage 1 to Stage 3 planning and test tree under `planning/` and `tests/`.

Why it matters: future Codex work needs one document that tells the truth about what exists now. This is the closest thing the repo has to that anchor.

### `docs/architecture/AZQ_ENGINE_SPEC.md`

This document is a faithful servant of the Medulla because it keeps each engine responsible for a distinct craft move, names proposal artifacts as non-canonical, and explicitly warns against a sixth public engine or stray side-script sprawl. That aligns well with live seams such as `azq/agenda/lineage.py` for lineage and `azq/formam/deliverable_storage.py` plus `azq/formam/map_storage.py` for accepted structural artifacts.

Why it matters: this is the clearest protection against scope drift into “generic planner with helpers.”

### `docs/architecture/AZQ_COMMAND_MODEL.md`

This is strong because it teaches the live CLI honestly from `azq/cli.py` and the engine CLIs, while still giving future direction without pretending that future behavior is already exposed. It protects the craft order and keeps future intelligence inside Finis, Formam, and Agenda.

Why it matters: command doctrine is where generic-tool drift often starts. This document mostly resists that.

### `docs/architecture/AZQ_FILESYSTEM_MODEL.md`

This document preserves the Medulla unusually well because it makes canonical artifacts, proposal artifacts, and archives legible as different classes of thing. That is exactly the boundary Medulla needs. It is also well matched to live canonical storage in `azq/finis/storage.py`, `azq/formam/deliverable_storage.py`, `azq/formam/map_storage.py`, `azq/agenda/task_storage.py`, and `azq/agenda/dag_storage.py`.

Why it matters: Medulla continuity becomes build-safe only when it is visible on disk.

### `docs/architecture/AZQ_BOOTSTRAP.md` and `README.md`

These two documents are strong because they stay close to repo truth. They preserve the current craft path, they say what is not yet live, and they keep the anti-task-manager frame visible. Their only notable weakness is mild overstatement around task logs.

## Partially Aligned Documents

### `docs/architecture/AZQ_PHILOSOPHY.md`

This document agrees with the Medulla in spirit and vocabulary. It explicitly distinguishes proposals from accepted craft, says the human accepts or rejects machine-shaped proposals, and resists multiplying engines. That is all good marrow.

Its weakness is that it does not bind those ideas tightly enough to live repo consequences. A builder reading only this file would not know the current accepted-state seams actually live in `data/finis/goals/`, `data/form/`, and `data/agenda/`, or that proposal artifacts are mostly future-only today.

Why that matters: it is good doctrine, but not a safe implementation authority by itself.

### `docs/architecture/AZQ_CRAFT_CHARTER.md`

The charter gets many important things right: stages are distinct, artifacts outrank abstractions, deliverables come before tasks, and the human holds judgment. Those points all support the Medulla.

The problem is that it is thin where the Medulla is sharpest. It does not clearly protect lineage mechanics, continuity mechanics, or the distinction between human-origin intent, model-origin suggestion, and accepted canonical state. The biggest doctrinal weakness is `Law 4 — Deletion Is First-Class`, especially when the live repo still exposes destructive deletion in `azq/scintilla/spark_delete.py` and the Medulla explicitly rejects destructive changes that erase continuity without stewardship.

Why that matters: a future builder could read this as permission to normalize deletion faster than stewardship, which is anti-Medulla even if it sounds tidy.

### `docs/architecture/AZQ_PLANNING_LOOP.md`

This document preserves one real Medulla value: visible reasoning before action. It is good on inspectability, human authorship, and the idea that intermediate artifacts let the human remain judge rather than spectator.

Its weakness is center of gravity. It talks more like a general visible-planning doctrine than like AZQ's craft spine. The main loop it teaches is `human -> ask for map -> misfit report -> move plan -> change plan -> chunked execution plan`, not `spark -> goal -> deliverable -> task -> action -> stewardship`. It also does not anchor those visible artifacts to accepted canonical state, nor to the live engine homes in `data/`.

Why that matters: technically correct planning advice can still weaken AZQ if it trains future Opifex work to build a generic planning artifact mill instead of a human-first LLM wrapper with lineage.

## Weak or Risky Documents

### `docs/architecture/AZQ_STATE_MODEL.md`

This is the weakest and riskiest architecture document in the repo.

What it supports:

- It tries to make object states, command states, and repository states visible.
- It does preserve some important distinctions, such as `proposed` versus `active`.

What is wrong:

- It still says “The current repository still uses `data/finis/goals.json` rather than fully normalized goal files,” but the live repo uses canonical goal Markdown via `azq/finis/storage.py`, `tests/test_stage1_wave_c.py`, and `data/finis/goals/*.md`.
- It teaches non-live commands such as `azq goal create`, `azq goal pause`, `azq goal resume`, `azq archive`, `azq prune`, `azq task complete`, `azq status`, and `azq doctor`, none of which exist in `azq/cli.py` today.
- It claims stronger live state behavior around archive, prune, in-progress task logs, and Domum-style repo health than the repo currently enforces.
- It describes task progression and stewardship surfaces as if the system can already protect them, while the live Agenda baseline mostly stops at stub task creation and goal-level DAG refresh in `azq/agenda/build.py` and `azq/agenda/dags.py`.

Why this is misalignment rather than simple staleness:

- It does not just lag the repo. It teaches a false canonical reality about accepted state and allowed transitions.
- That false state grammar would let future Codex work implement against imagined commands and imagined protections instead of the actual repository marrow.

### `docs/architecture/AZQ_Manifesto.md`

This document is not hostile to the Medulla, but it is too diffuse to protect it. It says AZQ is not a task manager and it keeps the human in judgment, which is good. But it is weak on build consequences: lineage, continuity, accepted-state distinction, and repo-truth boundaries are mostly implicit rather than explicit.

Why this is risky: elegance can hide doctrinal drift. A future contributor could quote this document to justify a beautiful but under-grounded planning system that does not actually preserve accepted state.

## Stale Statements That Matter

These are not all equal. Some are ordinary staleness. Some directly raise build risk.

| statement area | stale statement | why it matters |
| --- | --- | --- |
| `docs/architecture/AZQ_STATE_MODEL.md` | Finis still uses `data/finis/goals.json` as current storage. | This is directly false against `azq/finis/storage.py`, `tests/test_stage1_wave_c.py`, and `data/finis/goals/*.md`. It corrupts accepted-state understanding. |
| `docs/architecture/AZQ_STATE_MODEL.md` | `azq goal create`, `azq goal pause`, `azq goal resume`, `azq archive`, `azq prune`, `azq task complete`, `azq status`, and `azq doctor` are part of the state grammar. | These commands are not live in `azq/cli.py`. A builder could implement against the wrong public model. |
| `docs/architecture/AZQ_STATE_MODEL.md` | Strong live assumptions around archive, prune, repo health, and Domum readers. | The repo does not yet have `azq/domum/`, archive trees, or status/doctor readers. |
| `README.md`, `docs/architecture/AZQ_BOOTSTRAP.md`, `docs/architecture/AZQ_ENGINE_SPEC.md`, `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md` | Agenda task logs read as more live in the baseline than they actually are. | `azq/agenda/log_storage.py` exists, but `azq/agenda/build.py` does not create logs and checked-in `data/agenda/logs/` is empty. This is partial implementation, not full live workflow. |
| `pyproject.toml` | “starting with Cole Scintilla.” | This is low-severity staleness, but it weakens continuity between package identity and the actual Stage 3-capable repo. |

## Biggest Risks to Future Opifex / Codex Work

### 1. False canonical state from the state model

If future work treats `docs/architecture/AZQ_STATE_MODEL.md` as equally authoritative with Medulla and the implementation plan, it will build against non-live commands and false storage truth. That is the highest implementation risk in the doc layer.

### 2. Drift toward generic visible planning

`docs/architecture/AZQ_PLANNING_LOOP.md` has good instincts, but if it is used without the Medulla and engine boundaries, future work could prioritize maps, misfit reports, and execution plans as generic planning products rather than as engine-owned craft artifacts tied to accepted state.

### 3. Weak protection of proposal-vs-accepted state

The Medulla is sharp on this boundary, and the filesystem, engine, and command docs support it. But the charter, manifesto, and planning-loop layer do not protect it strongly enough. That matters because the live repo does not yet persist proposal families under `data/finis/`, `data/form/`, or `data/agenda/`; without crisp doctrine, future Codex work could start silently overwriting accepted artifacts instead of introducing explicit proposal seams.

### 4. Weak protection of continuity under deletion pressure

The live repo still has destructive spark deletion in `azq/scintilla/spark_delete.py`. The README correctly labels it temporary, and Medulla rejects it as a final pattern. The charter's deletion language weakens that warning rather than strengthening it.

### 5. Over-reading empty checked-in artifact areas as live maturity

The code supports Formam and Agenda, but the checked-in `data/form/` and `data/agenda/` trees are empty of canonical artifacts. The implementation plan handles this nuance well. Any future doc or worker that ignores it could mistake code capability for checked-in continuity.

## Recommended Repair Order

1. Repair `docs/architecture/AZQ_STATE_MODEL.md`.
Reason: it is the most misleading document in build terms and the likeliest to cause wrong implementations.

2. Repair `docs/architecture/AZQ_CRAFT_CHARTER.md`.
Reason: it is close to the marrow but under-protects continuity, proposal-vs-accepted state, and archive-first stewardship.

3. Repair `docs/architecture/AZQ_PLANNING_LOOP.md`.
Reason: it needs explicit subordination to the craft engines, the spark-to-action spine, and accepted canonical state so it cannot be mistaken for generic planning doctrine.

4. Tighten `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md`, `docs/architecture/AZQ_ENGINE_SPEC.md`, `docs/architecture/AZQ_COMMAND_MODEL.md`, `docs/architecture/AZQ_FILESYSTEM_MODEL.md`, `docs/architecture/AZQ_BOOTSTRAP.md`, and `README.md` around the same small issue: task logs are storage-capable but not yet part of the main live build flow.

5. Repair `docs/architecture/AZQ_Manifesto.md` and then harmonize it with `docs/architecture/AZQ_PHILOSOPHY.md`.
Reason: both are mostly spiritually aligned, but the manifesto is the more likely to be quoted in a way that hides the accepted-state and lineage requirements that Medulla makes explicit.

6. Update `pyproject.toml`.
Reason: low implementation risk, but cheap continuity gain.

## Closing Summary

The architecture-document layer still preserves the core mission of AZQ more often than it betrays it. The marrow is visible in the implementation plan, engine spec, command model, filesystem model, bootstrap guide, and README. Those documents describe AZQ as a human-first, file-backed wrapper for LLM-assisted work, and that matches the live repo under `azq/`, the Stage 1 to Stage 3 planning tree, and the regression tests.

The weakness is not total contradiction. The weakness is uneven protection. Some documents are sharp about intent, lineage, continuity, and accepted state. Others are thin, stale, or slightly off-center. The worst case is the state model, which is structurally ambitious but currently unsafe because it teaches false live reality. The subtler cases are the charter, manifesto, and planning loop, which often sound right but do not always defend the Medulla where it matters most.

Bottom line: future Opifex / Codex work should not proceed against the architecture layer as a flat consensus. It should proceed only with `AZQ_Medulla.md` as doctrine, the live repo as source of truth, and the implementation, engine, command, filesystem, bootstrap, and README documents as the practical architecture set. Until the risky documents are repaired, the architecture layer is only conditionally safe.
