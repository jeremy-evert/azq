# AZQ Implementation Plan Gap Report

## Executive Summary

`docs/architecture/AZQ_IMPLEMENTATION_PLAN.md` is no longer a good decomposition starting point as written. The repository already implements the Stage 1 to Stage 3 baseline in code, the stage planning tree records those stages as completed, and the regression tests lock in the canonical file-backed storage and CLI behavior across Finis, Formam, Agenda, and the Wave D Scintilla cleanup.

The main reality-check conclusions are:

| Area | Reality on disk |
| --- | --- |
| Stage 1 | Implemented in code and reflected in checked-in `data/finis/goals/`; `azq/finis/storage.py` owns canonical goal storage and legacy migration from `data/finis/goals.json`. |
| Stage 2 | Implemented in code; Formam has canonical deliverable and goal-map storage plus CLI wiring, but the checked-in `data/form/` snapshot is empty. |
| Stage 3 | Implemented in code; Agenda has canonical task, DAG, and task-log storage modules plus CLI wiring, but the checked-in `data/agenda/` snapshot is empty and task logs are not part of the live build flow. |
| Stage planning | `planning/stage_1/`, `planning/stage_2/`, and `planning/stage_3/` are already decomposed into waves and task/check files, and `codex/reports/codex_azq_task_status_report.md` records all 59 tracked tasks as done. |
| Biggest plan problem | The implementation plan still reads like a forward roadmap for work that the repo already completed for Stages 1 to 3. |

Before any further deliverable decomposition, `AZQ_IMPLEMENTATION_PLAN.md` should be revised into a rebased document: Stage 1 to Stage 3 as completed baseline, Stage 4+ as actual pending work, and known doc-vs-code mismatches called out explicitly.

## Repository Reality Snapshot

The current repository exposes a Stage 3-capable CLI through [`azq/cli.py`](../../azq/cli.py), [`azq/scintilla/cli.py`](../../azq/scintilla/cli.py), [`azq/finis/cli.py`](../../azq/finis/cli.py), [`azq/formam/cli.py`](../../azq/formam/cli.py), and [`azq/agenda/cli.py`](../../azq/agenda/cli.py). The live command surface matches the architecture docs and README: `capture`, `sparks`, `spark ...`, `fine`, `goals`, `goal ...`, `form ...`, and `agenda ...`.

The codebase is more modular than the implementation plan describes. Finis, Formam, and Agenda each have focused storage/schema layers rather than a single thin module:

| Subsystem | Key repo evidence |
| --- | --- |
| Scintilla | [`azq/scintilla/storage.py`](../../azq/scintilla/storage.py), [`azq/scintilla/sparks.py`](../../azq/scintilla/sparks.py), [`azq/scintilla/spark_view.py`](../../azq/scintilla/spark_view.py), [`azq/scintilla/spark_search.py`](../../azq/scintilla/spark_search.py), [`azq/scintilla/spark_delete.py`](../../azq/scintilla/spark_delete.py) |
| Finis | [`azq/finis/storage.py`](../../azq/finis/storage.py), [`azq/finis/fine.py`](../../azq/finis/fine.py), [`azq/finis/goal_manager.py`](../../azq/finis/goal_manager.py), [`azq/finis/goals.py`](../../azq/finis/goals.py) |
| Formam | [`azq/formam/deliverable_storage.py`](../../azq/formam/deliverable_storage.py), [`azq/formam/map_storage.py`](../../azq/formam/map_storage.py), [`azq/formam/build.py`](../../azq/formam/build.py), [`azq/formam/maps.py`](../../azq/formam/maps.py), [`azq/formam/storage.py`](../../azq/formam/storage.py) |
| Agenda | [`azq/agenda/task_storage.py`](../../azq/agenda/task_storage.py), [`azq/agenda/dag_storage.py`](../../azq/agenda/dag_storage.py), [`azq/agenda/log_storage.py`](../../azq/agenda/log_storage.py), [`azq/agenda/lineage.py`](../../azq/agenda/lineage.py), [`azq/agenda/build.py`](../../azq/agenda/build.py), [`azq/agenda/dags.py`](../../azq/agenda/dags.py), [`azq/agenda/storage.py`](../../azq/agenda/storage.py) |

Checked-in data tells a narrower story than code capability:

| Data area | Checked-in state |
| --- | --- |
| `data/scintilla/` | Populated with audio, transcripts, and spark JSON files. |
| `data/finis/goals/` | Populated with canonical goal Markdown files; `data/finis/goals.json` remains present as legacy input. |
| `data/form/` | Directories exist, but no checked-in deliverables or maps. |
| `data/agenda/` | Directories exist, but no checked-in tasks, DAGs, or logs. |

That means the repo contains Stage 2 and Stage 3 functionality, but the checked-in artifact snapshot is not itself currently `formed` or `actionable` in populated data terms.

## Plan-vs-Repo Mismatch Matrix

| Plan item or assumption | Repo evidence | Status | Notes |
| --- | --- | --- | --- |
| Stage 1 is roadmap work to normalize Finis storage | [`azq/finis/storage.py`](../../azq/finis/storage.py), [`planning/stage_1/overview.md`](../../planning/stage_1/overview.md), [`tests/test_stage1_wave_c.py`](../../tests/test_stage1_wave_c.py) | obsolete or superseded | Stage 1 is already implemented, tested, and planned as complete. |
| Stage 2 is roadmap work to introduce Formam | [`azq/formam/`](../../azq/formam), [`planning/stage_2/overview.md`](../../planning/stage_2/overview.md), [`tests/test_stage2_wave_c.py`](../../tests/test_stage2_wave_c.py) | obsolete or superseded | Formam already exists with canonical storage, parent validation, CLI routing, and regression coverage. |
| Stage 3 is roadmap work to introduce Agenda | [`azq/agenda/`](../../azq/agenda), [`planning/stage_3/overview.md`](../../planning/stage_3/overview.md), [`tests/test_stage3_wave_c.py`](../../tests/test_stage3_wave_c.py) | obsolete or superseded | Agenda already exists with task, DAG, and log storage plus CLI routing and tests. |
| Current repo still uses `data/finis/goals.json` rather than canonical goal files | [`docs/architecture/AZQ_STATE_MODEL.md`](../../docs/architecture/AZQ_STATE_MODEL.md), [`azq/finis/storage.py`](../../azq/finis/storage.py), [`data/finis/goals/`](../../data/finis/goals) | mismatch | The state model is stale here; code and data use canonical goal Markdown files with legacy JSON preserved as migration input. |
| Stage 3 baseline includes canonical task-log artifacts as active system-of-record output | [`azq/agenda/log_storage.py`](../../azq/agenda/log_storage.py), [`azq/agenda/build.py`](../../azq/agenda/build.py), [`data/agenda/logs/`](../../data/agenda/logs) | partially implemented | Log helpers exist, but `agenda build` does not create logs and no checked-in logs exist. |
| Formam and Agenda are still just stub writers | [`azq/formam/deliverable_storage.py`](../../azq/formam/deliverable_storage.py), [`azq/formam/map_storage.py`](../../azq/formam/map_storage.py), [`azq/agenda/task_storage.py`](../../azq/agenda/task_storage.py), [`azq/agenda/dag_storage.py`](../../azq/agenda/dag_storage.py) | mismatch | Build flows are stub-like, but storage, parsing, validation, lineage, and compatibility layers are already substantial. |
| Planning decomposition should happen later | [`planning/stage_1/`](../../planning/stage_1), [`planning/stage_2/`](../../planning/stage_2), [`planning/stage_3/`](../../planning/stage_3), [`codex/reports/codex_azq_task_status_report.md`](../../codex/reports/codex_azq_task_status_report.md) | mismatch | Deliverable/task decomposition already happened for Stages 1 to 3 and is recorded as complete. |
| Pyproject metadata is aligned with live repo scope | [`pyproject.toml`](../../pyproject.toml), [`README.md`](../../README.md) | mismatch | `pyproject.toml` still describes AZQ as “starting with Cole Scintilla,” which lags the Stage 3-capable codebase. |
| Archive-first direction is already reflected across the repo | [`azq/scintilla/spark_delete.py`](../../azq/scintilla/spark_delete.py), [`azq/cli.py`](../../azq/cli.py), [`README.md`](../../README.md) | partially implemented | Docs acknowledge `spark rm` is still destructive; no Domum or archive command family exists yet. |
| State model command examples match live CLI | [`docs/architecture/AZQ_STATE_MODEL.md`](../../docs/architecture/AZQ_STATE_MODEL.md), [`azq/cli.py`](../../azq/cli.py) | mismatch | The state model still references non-live commands like `azq goal create`, `azq goal pause`, `azq goal resume`, `azq archive`, and `azq prune`. |

## Findings by Subsystem

### CLI / command routing

- Implemented: the top-level CLI is split across engine routers in [`azq/cli.py`](../../azq/cli.py), [`azq/scintilla/router.py`](../../azq/scintilla/router.py), [`azq/finis/router.py`](../../azq/finis/router.py), [`azq/formam/router.py`](../../azq/formam/router.py), and [`azq/agenda/router.py`](../../azq/agenda/router.py).
- Implemented: the live command surface in code matches the architecture docs and README for Stage 1 to Stage 3.
- Missing: there is no `domum` package, no `azq status`, no `azq doctor`, no `azq archive ...`, and no non-destructive Scintilla archive path.
- Obsolete or superseded: older `azq task ...` and `azq dag ...` framing is explicitly rejected by the current CLI and by the Wave D planning/docs cleanup in [`planning/stage_3/wave_d/tasks.json`](../../planning/stage_3/wave_d/tasks.json).

### Scintilla

- Implemented: canonical path ownership and exact-id artifact lookup live in [`azq/scintilla/storage.py`](../../azq/scintilla/storage.py).
- Implemented: listing, exact-id inspection, search, and delete are covered by [`tests/test_stage3_wave_d.py`](../../tests/test_stage3_wave_d.py).
- Implemented: audio capture, transcript writing, and spark extraction exist in [`azq/scintilla/capture.py`](../../azq/scintilla/capture.py), [`azq/scintilla/transcribe.py`](../../azq/scintilla/transcribe.py), and [`azq/scintilla/extract.py`](../../azq/scintilla/extract.py).
- Partially implemented: Scintilla is file-backed and usable, but it still keeps destructive delete as the live retirement path through [`azq/scintilla/spark_delete.py`](../../azq/scintilla/spark_delete.py).
- Missing: the state model’s text-native capture and archive/prune flows are not implemented.
- Unclear / needs human decision: whether Scintilla should keep import-time Whisper loading in [`azq/scintilla/transcribe.py`](../../azq/scintilla/transcribe.py) as baseline behavior or treat that as pre-Stage-4 technical debt. The code-quality report flags it as an operational smell in [`codex/reports/code_complexity_and_maintainability_after_stage_3.md`](../../codex/reports/code_complexity_and_maintainability_after_stage_3.md).

### Finis

- Implemented: canonical goal storage, Markdown parsing/serialization, ID allocation, and legacy migration live in [`azq/finis/storage.py`](../../azq/finis/storage.py).
- Implemented: checked-in canonical goal files exist under [`data/finis/goals/`](../../data/finis/goals).
- Implemented: `fine`, `goals`, `goal add`, `goal close`, and `goal archive` are wired in [`azq/finis/cli.py`](../../azq/finis/cli.py).
- Partially implemented: `azq fine` shapes sparks into candidate goals, but only through simple interactive promotion, title cleanup, and dedupe in [`azq/finis/fine.py`](../../azq/finis/fine.py). The Stage 4 LLM-assisted shaping layer does not exist.
- Obsolete or superseded: Stage 1 as future work is no longer accurate.
- Mismatch: [`docs/architecture/AZQ_STATE_MODEL.md`](../../docs/architecture/AZQ_STATE_MODEL.md) still says the current repository uses `data/finis/goals.json`; that is no longer true for active storage.
- Data warning: the checked-in data includes at least one broken backlink. [`data/finis/goals/FINIS_001.md`](../../data/finis/goals/FINIS_001.md) references `2026-03-08_193337.json`, but that spark artifact is not present under [`data/scintilla/sparks/`](../../data/scintilla/sparks). That is repository data inconsistency, not a code capability gap.

### Formam

- Implemented: canonical deliverable storage, exact parent-goal validation, goal-map storage, and CLI routing exist across [`azq/formam/deliverable_storage.py`](../../azq/formam/deliverable_storage.py), [`azq/formam/map_storage.py`](../../azq/formam/maps.py), [`azq/formam/build.py`](../../azq/formam/build.py), and [`azq/formam/cli.py`](../../azq/formam/cli.py).
- Implemented: regression tests cover canonical schema, parsing, parent validation, CLI dispatch, and end-to-end build/list/show/map flow in [`tests/test_stage2_wave_c.py`](../../tests/test_stage2_wave_c.py).
- Partially implemented: `build_form` in [`azq/formam/build.py`](../../azq/formam/build.py) still creates one stub deliverable and a sparse goal map. That matches the Stage 2 baseline, not the deeper Formam vision.
- Partially implemented: the codebase still supports legacy `FORM_###` file compatibility in [`azq/formam/deliverable_storage.py`](../../azq/formam/deliverable_storage.py), even though canonical IDs are now `DELIV_###`.
- Missing: no LLM-assisted deliverable expansion, prioritization, or proposal artifact flow exists under `azq/formam/`.
- Codebase has grown beyond plan: Formam now has separate `paths`, `schemas`, `deliverable_storage`, `map_storage`, `storage`, `maps`, and `deliverables` modules, which the implementation plan does not describe.

### Agenda

- Implemented: canonical task, DAG, and log storage modules exist in [`azq/agenda/task_storage.py`](../../azq/agenda/task_storage.py), [`azq/agenda/dag_storage.py`](../../azq/agenda/dag_storage.py), and [`azq/agenda/log_storage.py`](../../azq/agenda/log_storage.py).
- Implemented: exact ancestry resolution is centralized in [`azq/agenda/lineage.py`](../../azq/agenda/lineage.py), which is a real Stage 3 Wave D seam not reflected in the implementation plan.
- Implemented: regression tests cover task schema, task parsing, parent-deliverable validation, DAG serialization, goal-level DAG reads, and refresh behavior in [`tests/test_stage3_wave_c.py`](../../tests/test_stage3_wave_c.py).
- Partially implemented: `build_agenda` in [`azq/agenda/build.py`](../../azq/agenda/build.py) still creates one stub task per deliverable. It does not decompose deliverables into commit-sized task sets.
- Partially implemented: `refresh_agenda_dag` in [`azq/agenda/dags.py`](../../azq/agenda/dags.py) derives deterministic edges from current task dependencies, but only for the exact deliverable path that was refreshed.
- Partially implemented: task-log helpers exist, but the live CLI does not expose start/complete flows and the build path does not create logs.
- Missing: no dedupe, no Codex preparation, no Agenda-owned execution reports, no LLM-assisted task shaping, and no public `agenda codex ...` family.
- Codebase has grown beyond plan: the plan talks about Stage 3 baseline at a higher level, but the repo now includes a lineage policy, focused path/schema/storage modules, and compatibility surfaces that would affect any further Agenda decomposition.

### Planning artifacts

- Implemented: stage planning exists for Stage 1 through Stage 3 in [`planning/stage_1/`](../../planning/stage_1), [`planning/stage_2/`](../../planning/stage_2), and [`planning/stage_3/`](../../planning/stage_3).
- Implemented: the stage overviews already treat those stages as completed baselines rather than future work, especially [`planning/stage_2/overview.md`](../../planning/stage_2/overview.md) and [`planning/stage_3/overview.md`](../../planning/stage_3/overview.md).
- Implemented: the status ledger in [`codex/reports/codex_azq_task_status_report.md`](../../codex/reports/codex_azq_task_status_report.md) records 59 tasks across 11 waves as done.
- Obsolete or superseded: using `AZQ_IMPLEMENTATION_PLAN.md` as the next decomposition input without first rebasing it would ignore already-completed planning work.
- Unclear / needs human decision: whether the planning tree should remain the canonical closeout record for completed stages, or whether `AZQ_IMPLEMENTATION_PLAN.md` should absorb that status and relegate stage planning to historical implementation records.

### Tests and validation

- Implemented: regression suites exist for Stage 1 Wave C, Stage 2 Wave C, Stage 3 Wave C, and Stage 3 Wave D in the exact files requested.
- Strong evidence: the tests treat canonical file formats and exact-id behavior as the contract. That is stronger evidence than aspirational architecture text when they disagree.
- Planning reality not captured by the implementation plan: the tests validate storage facades, compatibility aliases, exact lineage seams, and CLI dispatch behavior that the implementation plan does not mention.
- Missing: there is no cited test coverage here for Domum, `status`, `doctor`, archive-first replacements, or deeper LLM-assisted shaping.

### Data and storage layout

- Implemented: canonical directories for `scintilla`, `finis`, `form`, and `agenda` all exist under [`data/`](../../data).
- Implemented: the checked-in snapshot proves live Scintilla and Finis artifact families.
- Partially implemented: checked-in `data/form/` and `data/agenda/` directories exist but are empty, so the repo proves capability by code/tests rather than by committed Stage 2/3 sample artifacts.
- Partially implemented: `data/finis/goals.json` is still present, but code treats it as legacy input, not canonical storage.
- Missing: no `data/archive/`, no `data/artifacts/`, no `data/finis/proposals/`, no `data/form/proposals/`, no `data/agenda/proposals/`, no `data/agenda/reports/`, and no `data/agenda/runs/`.

## Items Likely Already Done

- Stage 1 Finis storage normalization is done in code, planning, and tests.
- Stage 2 Formam baseline is done in code, planning, and tests.
- Stage 3 Agenda baseline is done in code, planning, and tests.
- Top-level CLI routing has already been split into engine-specific routers.
- Wave D cleanup seams already exist for Agenda lineage and Scintilla storage.

## Items Partially Done

- `azq fine` does basic spark-to-goal shaping, but not the planned LLM-assisted questioning and proposal workflow.
- `azq form build` creates a usable stub deliverable and goal map, but not deliverable expansion or prioritization.
- `azq agenda build` creates a usable stub task, and `azq agenda dag` creates a DAG artifact, but not commit-sized decomposition, dedupe, or Codex preparation.
- Agenda task-log storage exists as a module, but task logs are not yet part of the live Stage 3 build/inspection flow.
- Archive-first direction is acknowledged, but destructive spark deletion is still live and there is no Domum engine yet.

## Items Missing

- `azq/domum/`
- `azq status`
- `azq doctor`
- archive command family and `data/archive/`
- artifact publication layer and `data/artifacts/`
- Finis proposal/note artifacts and LLM shaping modules
- Formam proposal/expansion/prioritization modules
- Agenda decomposition/dedupe/Codex modules
- text-native capture path in Scintilla
- live pause/resume/supersede goal commands described by the state model

## Items Likely Obsolete or Superseded

- Stage 1, Stage 2, and Stage 3 as forward implementation stages in `AZQ_IMPLEMENTATION_PLAN.md`
- any future decomposition that starts by re-decomposing completed Stage 1 to Stage 3 work
- stale state-model claims that Finis still uses `goals.json` as active storage
- older command-model examples outside the current `azq agenda ...` family

## Items Requiring Human Decision

- Whether `AZQ_IMPLEMENTATION_PLAN.md` should become a baseline-plus-next-work document or remain a historical roadmap with explicit “completed” markings added.
- Whether legacy compatibility layers such as `FORM_###` support in [`azq/formam/deliverable_storage.py`](../../azq/formam/deliverable_storage.py) should remain part of the supported baseline or be retired in a later cleanup.
- Whether Stage 3 should be considered complete without automatic task-log creation in the live build flow.
- Whether the checked-in repository should include canonical sample Formam and Agenda artifacts, or whether tests alone are the intended proof for Stage 2 and Stage 3 artifact families.

## Recommended Revisions to AZQ_IMPLEMENTATION_PLAN.md

- Rebase the document so Stage 1, Stage 2, and Stage 3 are described as completed baseline, not upcoming work.
- Add a short “current repository truth” section that explicitly separates:
  - code capability
  - checked-in data snapshot
  - future architecture direction
- Update the plan to acknowledge the current module boundaries actually on disk:
  - `finis/storage.py`
  - `formam/paths.py`, `schemas.py`, `deliverable_storage.py`, `map_storage.py`, `storage.py`
  - `agenda/paths.py`, `schemas.py`, `task_storage.py`, `dag_storage.py`, `log_storage.py`, `lineage.py`, `storage.py`
  - `scintilla/storage.py`
- Correct stale assumptions imported from the state model, especially the claim that Finis still uses `data/finis/goals.json` as the live store.
- Mark Agenda task logs as “storage implemented, live task-build integration still limited” unless the code is changed first.
- Make Stage 4 the real next implementation stage, with Stage 5+ following from that.
- Add a brief “planning already completed” note that points to [`planning/stage_1/`](../../planning/stage_1), [`planning/stage_2/`](../../planning/stage_2), [`planning/stage_3/`](../../planning/stage_3), and [`codex/reports/codex_azq_task_status_report.md`](../../codex/reports/codex_azq_task_status_report.md).
- Add a small “known repo data inconsistencies” note or at least avoid describing checked-in data as fully healthy. The broken backlink from [`data/finis/goals/FINIS_001.md`](../../data/finis/goals/FINIS_001.md) to a missing Scintilla spark is one concrete example.

## Recommended Next Step Before Deliverable Decomposition

Do not decompose new deliverables from the current implementation plan as-is. First revise `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md` into a rebased plan that treats Stage 1 through Stage 3 as completed repo reality, explicitly records the remaining partial gaps, and narrows the forward scope to genuine pending work: deeper Finis/Formam/Agenda shaping, Domum, archive/status/doctor, and deletion-to-archive replacement.

That revised plan should then be checked against the current stage planning tree so later deliverable extraction starts from one truthful baseline instead of from overlapping historical roadmaps.

## Closing Summary

This report was grounded against the live architecture docs, README, `pyproject.toml`, the current `azq/` implementation, the `planning/` stage and wave artifacts, the cited regression tests, the checked-in `data/` tree, and the two existing Codex reports.

The biggest mismatches are:

- the implementation plan still treats Stage 1 to Stage 3 as future roadmap work even though the repo has already implemented, planned, and tested those stages
- the state model still contains stale Finis and command-surface claims that no longer match the repository
- Agenda task logs exist as storage helpers, but the checked-in repo and live build flow do not support the stronger “task logs are already active baseline artifacts” reading

Before stage deliverables are extracted, the implementation plan should be rebased to current repo reality and aligned with the completed planning artifacts so later decomposition starts from a single truthful source.
