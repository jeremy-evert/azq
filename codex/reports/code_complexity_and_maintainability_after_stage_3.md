# Code Complexity And Maintainability After Stage 3

## Scope
- Date: 2026-03-19
- Report location target: `codex_reports/code_complexity_and_maintainability_after_stage_3.md`
- Included: repository-owned source, docs, manifests, tests, sample data, existing reports, and generated project data under `data/`.
- Excluded from line counting and maintainability analysis: `.git/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.azq_codex_runs/`, and `.azq_codex_progress_*.json`.
- Line counts are physical lines per file. Binary assets are marked `binary` instead of forcing a fake LOC value.

## Executive Summary
- Maintained file inventory in scope: 173 files.
- Python code in `azq/` and `tests/`: 5,598 lines total. Application code in `azq/`: 4,437 lines.
- The codebase is small enough to refactor without a rewrite, but several modules are already acting as mixed parser + storage + compatibility + validation layers.
- The dominant smell is not raw size; it is boundary leakage and compatibility shims that duplicate APIs across modules, especially in `finis`, `formam`, and `agenda`.
- Immediate refactor targets are the storage/facade layers and module import surfaces. The CLI flows and thin builders are less elegant, but still workable.

## Immediate Refactor Candidates
- `azq/formam/storage.py` is a compatibility facade that re-exports and reshapes goal-map behavior on top of `map_storage.py` and `deliverable_storage.py`. That split preserves backwards compatibility, but it also creates two public truths for the same subsystem and makes future edits risky.
- `azq/agenda/storage.py` uses wildcard re-exports from multiple modules. That flattens subsystem boundaries and makes it harder to know where behavior actually lives, which raises refactor risk and complicates import hygiene.
- `azq/finis/storage.py`, `azq/formam/deliverable_storage.py`, `azq/formam/map_storage.py`, and `azq/agenda/task_storage.py` each mix normalization, parsing, serialization, filesystem access, and parent validation. Those are coherent by feature, but not by responsibility.
- `azq/agenda/lineage.py` couples Agenda directly to both Formam and Finis persistence layers. That is a practical seam today, but it makes Agenda refactors dependent on storage details in sibling domains.
- `azq/scintilla/transcribe.py` loads Whisper models at import time and prints at import time. That is an immediate operational smell because module import has side effects and expensive startup cost.

## Difficult But Still Workable
- The markdown-based persistence pattern is repetitive across domains, but it is internally consistent. Refactoring toward shared parser/serializer helpers is feasible because file formats are simple and tests exist.
- Builder modules like `azq/formam/build.py` and `azq/agenda/build.py` are thin and readable. They are not a smell by themselves, though they currently depend on storage-heavy modules instead of domain service abstractions.
- CLI routing is simple and flat. It lacks stronger command abstractions, but the current size means it is still easy to evolve incrementally.
- Tests are fairly large and integration-heavy, which makes them slower to reason about, but they do provide useful regression coverage for canonical formats and migration behavior.

## Maintainability Assessment
### Boundary Quality
- Domain separation is visible: `finis` for goals, `formam` for deliverables/maps, `agenda` for tasks/DAGs, and `scintilla` for capture/transcription/sparks. That is a good top-level decomposition.
- Inside each domain, boundaries are weaker than the folder names suggest. Storage modules often own schema normalization, text parsing, serialization, ID generation, and validation together.
- Compatibility facades blur ownership. A caller can often import from package roots, facade modules, or storage modules and get overlapping behavior.
- Cross-domain lineage resolution is explicit, which is good, but it is implemented as direct storage-to-storage calls rather than narrower interfaces.

### Refactorability
- Overall refactorability is moderate. The system is small, naming is mostly consistent, and the tests encode expected behavior for the canonical file formats.
- The main refactor hazard is import-surface ambiguity. Before deeper changes, the project should define one authoritative public API per subsystem and deprecate the rest.
- The second hazard is duplicated markdown parsing patterns across goal, deliverable, map, and task artifacts. A refactor can likely extract shared parsing helpers, but only after locking down the intended canonical schemas.
- The third hazard is side-effectful runtime modules in Scintilla, where import order and environment capabilities matter more than they should.

### Stronger Areas
- ID schemes are predictable and human-readable.
- Canonical record normalization is deliberate and conservative.
- File-backed artifacts are inspectable and diff-friendly.
- The tests show the intended migration path and canonical storage rules clearly.

### Weaker Areas / Code Smells
- Wildcard re-export facades.
- Multiple modules representing nearly the same storage API.
- Parsing/serialization code repeated with minor structural differences.
- Direct persistence-layer coupling across domains.
- Import-time side effects in Scintilla.
- One large operational script, `azq_codex_task_runner.py`, carrying parsing, prompting, process execution, reporting, and state management in one file.

## Highest-Risk Python Files By Size / Responsibility
| File | Lines | Why it matters |
| --- | ---: | --- |
| `azq_codex_task_runner.py` | 768 | Monolithic operational script spanning orchestration, prompt building, subprocess execution, checks, persistence, and reporting. |
| `azq/finis/storage.py` | 415 | Mixed parser, serializer, migration, path ownership, ID generation, and persistence logic. |
| `azq/agenda/task_storage.py` | 369 | Mixed markdown parsing, storage, validation, lineage application, and ID allocation. |
| `azq/formam/deliverable_storage.py` | 356 | Mixed canonical parsing, persistence, legacy compatibility, and parent validation. |
| `azq/formam/map_storage.py` | 294 | Mixed normalization, markdown parsing, dependency-edge translation, and persistence. |
| `azq/agenda/schemas.py` | 248 | Central schema logic; important, but currently broad enough that changes can ripple widely. |
| `azq/finis/fine.py` | 209 | Workflow logic and interactive behavior are bundled together without stronger service boundaries. |
| `azq/formam/storage.py` | 190 | Compatibility shim that increases API duplication and boundary confusion. |

## Folder Depth Report
| Folder | Max nested folder depth inside it |
| --- | ---: |
| `.` | 3 |
| `azq` | 1 |
| `azq/agenda` | 0 |
| `azq/finis` | 0 |
| `azq/formam` | 0 |
| `azq/scintilla` | 0 |
| `azq.egg-info` | 0 |
| `codex_reports` | 0 |
| `codex_support` | 0 |
| `data` | 2 |
| `data/agenda` | 1 |
| `data/agenda/dags` | 0 |
| `data/agenda/logs` | 0 |
| `data/agenda/tasks` | 0 |
| `data/finis` | 1 |
| `data/finis/goals` | 0 |
| `data/form` | 1 |
| `data/form/deliverables` | 0 |
| `data/form/maps` | 0 |
| `data/scintilla` | 1 |
| `data/scintilla/audio` | 0 |
| `data/scintilla/sparks` | 0 |
| `data/scintilla/transcripts` | 0 |
| `documents` | 0 |
| `tests` | 0 |

## File Line Count Report
| File | Lines |
| --- | ---: |
| `.gitignore` | 56 |
| `AZQ_BOOTSTRAP.md` | 509 |
| `AZQ_BUILD_TASKS_STAGE_1.md` | 476 |
| `AZQ_BUILD_TASKS_STAGE_1_WAVE_A.json` | 173 |
| `AZQ_BUILD_TASKS_STAGE_1_WAVE_B.json` | 202 |
| `AZQ_BUILD_TASKS_STAGE_1_WAVE_C.json` | 93 |
| `AZQ_BUILD_TASKS_STAGE_2.md` | 563 |
| `AZQ_BUILD_TASKS_STAGE_2_WAVE_A.json` | 270 |
| `AZQ_BUILD_TASKS_STAGE_2_WAVE_B.json` | 167 |
| `AZQ_BUILD_TASKS_STAGE_2_WAVE_C.json` | 100 |
| `AZQ_BUILD_TASKS_STAGE_2_WAVE_D.json` | 205 |
| `AZQ_BUILD_TASKS_STAGE_3.md` | 621 |
| `AZQ_BUILD_TASKS_STAGE_3_WAVE_A.json` | 288 |
| `AZQ_BUILD_TASKS_STAGE_3_WAVE_B.json` | 169 |
| `AZQ_BUILD_TASKS_STAGE_3_WAVE_C.json` | 74 |
| `AZQ_BUILD_TASKS_STAGE_3_WAVE_D.json` | 140 |
| `AZQ_CHECKS_STAGE_1_WAVE_A.json` | 130 |
| `AZQ_CHECKS_STAGE_1_WAVE_B.json` | 194 |
| `AZQ_CHECKS_STAGE_1_WAVE_C.json` | 93 |
| `AZQ_CHECKS_STAGE_2_WAVE_A.json` | 198 |
| `AZQ_CHECKS_STAGE_2_WAVE_B.json` | 183 |
| `AZQ_CHECKS_STAGE_2_WAVE_C.json` | 102 |
| `AZQ_CHECKS_STAGE_2_WAVE_D.json` | 199 |
| `AZQ_CHECKS_STAGE_3_WAVE_A.json` | 275 |
| `AZQ_CHECKS_STAGE_3_WAVE_B.json` | 190 |
| `AZQ_CHECKS_STAGE_3_WAVE_C.json` | 89 |
| `AZQ_CHECKS_STAGE_3_WAVE_D.json` | 178 |
| `AZQ_CODEX_PROMPT_TEMPLATE_STAGE_1.md` | 168 |
| `AZQ_CODEX_RUNBOOK_STAGE_1_WAVE_A.md` | 419 |
| `AZQ_CODEX_RUNBOOK_STAGE_2_WAVE_A.md` | 469 |
| `AZQ_COMMAND_MODEL.md` | 727 |
| `AZQ_CRAFT_CHARTER.md` | 348 |
| `AZQ_ENGINE_SPEC.md` | 433 |
| `AZQ_FILESYSTEM_MODEL.md` | 405 |
| `AZQ_IMPLEMENTATION_PLAN.md` | 539 |
| `AZQ_Manifesto.md` | 749 |
| `AZQ_PHILOSOPHY.md` | 792 |
| `AZQ_STAGE_1_WAVE_C_CLOSEOUT.md` | 114 |
| `AZQ_STATE_MODEL.md` | 963 |
| `LICENSE` | 1 |
| `README.md` | 420 |
| `azq/__init__.py` | 0 |
| `azq/agenda/__init__.py` | 25 |
| `azq/agenda/build.py` | 80 |
| `azq/agenda/cli.py` | 52 |
| `azq/agenda/dag_storage.py` | 137 |
| `azq/agenda/dags.py` | 146 |
| `azq/agenda/lineage.py` | 80 |
| `azq/agenda/log_storage.py` | 163 |
| `azq/agenda/paths.py` | 110 |
| `azq/agenda/router.py` | 5 |
| `azq/agenda/schemas.py` | 248 |
| `azq/agenda/storage.py` | 29 |
| `azq/agenda/task_storage.py` | 369 |
| `azq/agenda/tasks.py` | 112 |
| `azq/cli.py` | 47 |
| `azq/finis/__init__.py` | 0 |
| `azq/finis/cli.py` | 85 |
| `azq/finis/fine.py` | 209 |
| `azq/finis/goal_manager.py` | 48 |
| `azq/finis/goals.py` | 21 |
| `azq/finis/router.py` | 5 |
| `azq/finis/storage.py` | 415 |
| `azq/formam/__init__.py` | 36 |
| `azq/formam/build.py` | 116 |
| `azq/formam/cli.py` | 58 |
| `azq/formam/deliverable_storage.py` | 356 |
| `azq/formam/deliverables.py` | 106 |
| `azq/formam/map_storage.py` | 294 |
| `azq/formam/maps.py` | 133 |
| `azq/formam/paths.py` | 80 |
| `azq/formam/router.py` | 5 |
| `azq/formam/schemas.py` | 100 |
| `azq/formam/storage.py` | 190 |
| `azq/scintilla/__init__.py` | 1 |
| `azq/scintilla/capture.py` | 126 |
| `azq/scintilla/cli.py` | 84 |
| `azq/scintilla/extract.py` | 35 |
| `azq/scintilla/router.py` | 5 |
| `azq/scintilla/spark_delete.py` | 20 |
| `azq/scintilla/spark_search.py` | 32 |
| `azq/scintilla/spark_view.py` | 42 |
| `azq/scintilla/sparks.py` | 34 |
| `azq/scintilla/storage.py` | 106 |
| `azq/scintilla/transcribe.py` | 92 |
| `azq.egg-info/PKG-INFO` | 434 |
| `azq.egg-info/SOURCES.txt` | 57 |
| `azq.egg-info/dependency_links.txt` | 1 |
| `azq.egg-info/entry_points.txt` | 2 |
| `azq.egg-info/requires.txt` | 3 |
| `azq.egg-info/top_level.txt` | 1 |
| `azq_codex_stage1_task_runner.py` | 9 |
| `azq_codex_task_runner.py` | 768 |
| `codex_reports/codex_azq_task_status_report.md` | 249 |
| `codex_support/codex_framework.json` | 121 |
| `codex_support/codex_propmt_advice.md` | 90 |
| `data/finis/goals/FINIS_001.md` | 10 |
| `data/finis/goals/FINIS_002.md` | 10 |
| `data/finis/goals/FINIS_003.md` | 10 |
| `data/finis/goals/FINIS_004.md` | 9 |
| `data/finis/goals/FINIS_005.md` | 10 |
| `data/finis/goals/FINIS_006.md` | 10 |
| `data/finis/goals/FINIS_007.md` | 9 |
| `data/finis/goals/FINIS_008.md` | 9 |
| `data/finis/goals/FINIS_009.md` | 9 |
| `data/finis/goals/FINIS_010.md` | 9 |
| `data/finis/goals/FINIS_011.md` | 9 |
| `data/finis/goals/FINIS_012.md` | 9 |
| `data/finis/goals/FINIS_013.md` | 9 |
| `data/finis/goals/FINIS_014.md` | 9 |
| `data/finis/goals/FINIS_015.md` | 10 |
| `data/finis/goals/FINIS_016.md` | 10 |
| `data/finis/goals/FINIS_017.md` | 10 |
| `data/finis/goals/FINIS_018.md` | 10 |
| `data/finis/goals/FINIS_019.md` | 10 |
| `data/finis/goals/FINIS_020.md` | 10 |
| `data/finis/goals/FINIS_021.md` | 10 |
| `data/finis/goals/FINIS_022.md` | 10 |
| `data/finis/goals/FINIS_023.md` | 9 |
| `data/finis/goals/FINIS_024.md` | 9 |
| `data/finis/goals/FINIS_025.md` | 9 |
| `data/finis/goals/FINIS_026.md` | 9 |
| `data/finis/goals/FINIS_027.md` | 9 |
| `data/finis/goals.json` | 215 |
| `data/scintilla/audio/2026-03-08_195132.wav` | binary |
| `data/scintilla/audio/2026-03-09_083032.wav` | binary |
| `data/scintilla/audio/2026-03-09_083151.wav` | binary |
| `data/scintilla/audio/2026-03-09_090132.wav` | binary |
| `data/scintilla/audio/2026-03-09_090255.wav` | binary |
| `data/scintilla/audio/2026-03-09_090431.wav` | binary |
| `data/scintilla/sparks/2026-03-08_195132.json` | 6 |
| `data/scintilla/sparks/2026-03-09_083032.json` | 6 |
| `data/scintilla/sparks/2026-03-09_083151.json` | 10 |
| `data/scintilla/sparks/2026-03-09_090132.json` | 10 |
| `data/scintilla/sparks/2026-03-09_090255.json` | 14 |
| `data/scintilla/sparks/2026-03-09_090431.json` | 26 |
| `data/scintilla/transcripts/2026-03-08_195132.txt` | 1 |
| `data/scintilla/transcripts/2026-03-09_083032.txt` | 1 |
| `data/scintilla/transcripts/2026-03-09_083151.txt` | 1 |
| `data/scintilla/transcripts/2026-03-09_090132.txt` | 1 |
| `data/scintilla/transcripts/2026-03-09_090255.txt` | 1 |
| `data/scintilla/transcripts/2026-03-09_090431.txt` | 1 |
| `documents/Bacon_Novum Organum_Bk1.pdf` | binary |
| `documents/The_Five_Canons_of_Rhetoric.pdf` | binary |
| `documents/didascaliconmedi00hugh.pdf` | binary |
| `pyproject.toml` | 33 |
| `run_next_task_in_current_wave.sh` | 283 |
| `tests/test_stage1_wave_c.py` | 289 |
| `tests/test_stage2_wave_c.py` | 341 |
| `tests/test_stage3_wave_c.py` | 378 |
| `tests/test_stage3_wave_d.py` | 153 |
