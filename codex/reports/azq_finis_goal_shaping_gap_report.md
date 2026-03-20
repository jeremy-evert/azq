# AZQ Finis Goal Shaping Gap Report

## Executive Summary

Finis is live today as a basic spark-to-goal promotion layer, not yet as a richer human-first goal-shaping layer. The actual path on disk is narrow: `azq fine` loads extracted spark text from `data/scintilla/sparks/`, cleans it into short candidate titles, skips candidates whose spark source already appears in a canonical goal's `derived_from`, asks a simple `Accept goal? [y/n]` prompt, and writes accepted results directly to canonical goal files under `data/finis/goals/`.

That means Finis already has a real canonical goal store and a real promotion loop, but it does not yet preserve a durable pre-goal review layer. There is no visible Finis artifact family for proposals, reviews, questions, usefulness notes, tractability notes, or intent packages. Candidate text exists only in transient CLI interaction. Accepted canonical goal text exists durably. The smallest practical deepening is therefore not a redesign. It is to add one durable Finis review artifact layer and make `azq fine` promote from that review state into the existing canonical goal files.

## Current Live Finis Goal Shaping

| Area | Live behavior |
| --- | --- |
| Command entry | `azq/finis/cli.py` routes `azq fine` to `run_fine()` after `ensure_canonical_goals_migrated()`. |
| Spark input | `azq/finis/fine.py` reads every `*.json` file under `data/scintilla/sparks/` and loads each `spark` string with `source=file.stem`. |
| Candidate shaping | `clean_goal_text()` strips a small set of spoken prefixes, normalizes whitespace, and capitalizes the first character. |
| Deduping | `propose_goals()` loads canonical goals through `azq/finis/storage.py`, compares candidate titles to existing goal titles with `difflib.SequenceMatcher`, and skips candidates at or above `TITLE_DEDUPE_THRESHOLD = 0.39`. |
| Source reuse rule | `get_used_sources()` marks any spark source already present in a goal's `derived_from`; `propose_goals()` skips later sparks from those sources entirely. |
| Human review | `confirm_goals()` prints `Candidate Goals` and asks only `Accept goal? [y/n]` for each candidate. |
| Canonical write | `run_fine()` writes accepted candidates directly to `data/finis/goals/FINIS_###.md` with `status=active`, `description=""`, `created=<today>`, and `derived_from=[source]`. |

Plainly, `azq fine` today is a heuristic spark-title promotion command. It is not an LLM-assisted shaping flow in code.

The live canonical goal format is owned by `azq/finis/storage.py`. It writes one Markdown file per goal with:

- `goal_id`
- `title`
- `status`
- `created`
- `derived_from`
- `## Description`

The checked-in data snapshot matches that baseline. `data/finis/` currently contains only `goals.json` and `goals/`. It does not contain `proposals/`, `reviews/`, `questions/`, or `intent_packages/`.

## Failure or Limitation For This Workflow

For Stage 4 goal shaping, the main limitation is that Finis currently collapses review into immediate canonical promotion.

| Limitation | Repo-grounded evidence |
| --- | --- |
| No durable pre-goal review artifact | `data/finis/` has only `goals/`; `azq/finis/storage.py` only manages canonical goals and legacy migration. |
| No richer review states | `confirm_goals()` supports only accept or skip. |
| No durable candidate text | Candidates are built in memory in `propose_goals()` and disappear after the CLI session unless accepted as canonical goals. |
| No human revision layer | `run_fine()` writes the cleaned candidate title directly as canonical `title`; there is no separate revised text field or artifact. |
| No narrowing-question support | No Finis module or storage path records questions. |
| No usefulness or tractability judgment | Canonical goals only store `title`, `status`, `created`, `description`, and `derived_from`. |
| No explicit human/model boundary | The Medulla and Engine Spec require visible separation between proposal state and accepted canonical state, but Finis currently has only spark input and canonical goal output. |

This matters because Stage 4 is specifically about deepening Finis as the human-intent layer, and the current path does not preserve enough review continuity to do that.

## Missing Capability

Finis currently preserves only part of the distinction the architecture calls for.

| Distinction | Current repo reality |
| --- | --- |
| Raw spark text | Yes, at the Scintilla layer in `data/scintilla/sparks/*.json`, with transcript context in `data/scintilla/transcripts/*.txt`. |
| Candidate goal text | Only ephemerally inside `azq/finis/fine.py` during one `azq fine` run. No durable Finis artifact stores it. |
| Accepted canonical goal text | Yes, in `data/finis/goals/FINIS_###.md`. |

Conservative judgment: AZQ does preserve a spark-to-goal lineage link today through `derived_from`, but Finis does not durably preserve the full Stage 4 boundary between raw spark text, candidate proposal text, human revision text, and accepted canonical goal text.

Missing Stage 4-capable Finis behavior:

- durable review artifacts before canonical goal creation
- visible review states beyond accept-or-skip
- explicit human revision text distinct from candidate text
- narrowing questions tied to exact spark and review context
- usefulness and tractability notes
- a provenance contract that keeps pre-acceptance text visibly distinct from accepted goal text

## Smallest Practical Deepening

The narrowest safe next deepening is to keep `azq fine` as the entry point and insert one durable review layer inside Finis.

Recommended minimal shape:

| Item | Minimal recommendation |
| --- | --- |
| New artifact family | Add `data/finis/reviews/` first. |
| Command posture | Keep `azq fine`; deepen its flow instead of inventing a new engine or broad new command family. |
| Review record contents | Store exact spark source ids, raw spark excerpts, candidate goal text, optional human revision text, review status, and accepted `goal_id` when promoted. |
| Promotion rule | Only write `data/finis/goals/FINIS_###.md` after an explicit accept step from a review artifact. |
| Canonical goal storage | Reuse `azq/finis/storage.py` and the existing Markdown goal format unchanged for the first pass. |
| LLM posture | Do not require model integration in the first repair. First create the durable boundary that Stage 4 needs. |

Why this is the smallest useful deepening:

- it keeps Finis inside its current engine boundary
- it does not redesign canonical goal storage
- it gives `azq fine` a real human-first review seam
- it creates the provenance boundary Stage 4 needs before adding richer proposal or question features

Conservative judgment: `data/finis/reviews/` is the best first addition because `planning/stage_4/deliverables.json` already marks the richer review surface as partial and makes later proposal, question, and note work depend on it directly or indirectly.

## Likely File Touch Points

| File | Why it is the likely seam |
| --- | --- |
| `azq/finis/fine.py` | Current candidate generation, review prompt, and canonical write flow all live here. |
| `azq/finis/storage.py` | Natural home for review-path helpers, review serialization, and path constants alongside existing Finis storage rules. |
| `azq/finis/cli.py` | May need only light changes if `azq fine` gains richer review options or resume behavior. |
| `azq/cli.py` | Only if the printed command list needs to reflect a refined Finis surface. |
| `azq/finis/goals.py` | Possibly useful if accepted goals should surface review linkage or richer display later; not necessarily needed for the first step. |
| `azq/finis/goal_manager.py` | Probably not required for the first deepening unless manual goal creation is brought into the same review contract. |
| `data/finis/reviews/` | New durable review artifacts. |

## Minimum Test Surface

The minimum new test surface should prove the new boundary without re-testing Stage 1 storage as if it were new.

| Test | Why it is enough |
| --- | --- |
| `azq fine` writes a review artifact instead of immediately collapsing candidate text into transient CLI-only state | Proves the new Stage 4 seam exists. |
| Review artifact preserves spark source id, raw spark excerpt, candidate text, and review status separately | Proves provenance and text-boundary preservation. |
| Accepting a reviewed candidate still writes a canonical `FINIS_###.md` goal through existing storage helpers | Proves Stage 1 storage stays the acceptance target. |
| Accepted goal keeps lineage back to the originating spark and review artifact | Proves continuity across the new seam. |

Likely test home: a new Stage 4 Finis test file is cleaner than overloading `tests/test_stage1_wave_c.py`, though the existing `test_fine_writes_canonical_goal_with_derived_from_backlink` is the current baseline contract to preserve.

## Stage 4 Deliverable Mapping

| Deliverable | Relation to this gap |
| --- | --- |
| `S4_DELIV_001` Richer Finis goal review surface | Most direct match. The current repo has only a one-step accept-or-skip review loop. |
| `S4_DELIV_006` Provenance-preserving human and model intent lineage | Also direct. The repo has `derived_from` lineage, but not the fuller Stage 4 text-boundary contract. |
| `S4_DELIV_002` Finis proposal artifact flow | Still missing. A review artifact layer is the smallest practical precursor without forcing a bigger redesign first. |
| `S4_DELIV_003` Narrowing-question support | Missing and downstream of a durable review/proposal seam. |
| `S4_DELIV_004` Usefulness and tractability notes | Missing and easier once review artifacts exist. |
| `S4_DELIV_005` Intent package for downstream model-facing work | Missing and premature until review and provenance boundaries exist. |

## Recommended Next Step

Deepen `azq fine` so it writes and updates durable Finis review artifacts under `data/finis/reviews/`, with separate fields or sections for:

- spark source id
- raw spark text
- candidate goal text
- optional human revision text
- review status
- accepted canonical goal id once promoted

Then keep canonical goal creation exactly where it already belongs: `azq/finis/storage.py` writing `data/finis/goals/FINIS_###.md`.

That is the narrowest safe next implementation step because it strengthens intent, lineage, and continuity without changing Finis into a different engine.

## Closing Summary

Live Finis goal shaping is real, but thin. `azq fine` currently reads spark JSON, cleans each spark into a short candidate title, prompts `Accept goal? [y/n]`, and writes accepted candidates directly into canonical goal files.

What is missing for Stage 4 is not another engine. It is a durable pre-canonical review layer inside Finis. The smallest practical deepening is to add `data/finis/reviews/` and teach `azq fine` to promote from review artifacts into the existing goal store. That most directly supports `S4_DELIV_001` and `S4_DELIV_006`, while setting up the missing proposal, question, notes, and intent-package work later.
