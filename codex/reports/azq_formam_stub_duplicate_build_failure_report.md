# AZQ Formam Stub Duplicate Build Failure Report

## Executive Summary

`azq form build <goal_id>` is a thin Stage 2 baseline writer, not a meaningful deliverable-shaping flow. In live code, `azq/formam/build.py` validates one exact active parent goal, allocates the next global `DELIV_###` id, creates one stub deliverable whose `title` is copied directly from the goal title, writes that deliverable to `data/form/deliverables/`, then refreshes one goal map at `data/form/maps/GOAL_<goal_id>_MAP.md` from all deliverables currently attached to that goal.

That means current Formam behavior is stub-only. It does not decompose one goal into multiple meaningful artifact boundaries, and it does not try to detect whether the goal has already been built. Re-running `azq form build FINIS_028` is therefore not idempotent today: the code path will allocate a fresh `DELIV_###`, write another same-title stub deliverable for the same goal, and refresh the goal map so both deliverables appear with empty dependency edges.

The failure is a combination of stub generation strategy, missing goal-to-deliverable shaping logic, and a missing rebuild guard. The smallest practical fix is not a Formam redesign. It is to keep the current Stage 2 stub baseline, but make `build_form()` idempotent for goals that already have canonical deliverables by returning the existing deliverable set and refreshing the map instead of always creating a new `DELIV_###` record.

Conservative judgment: the duplicate-build artifacts from the reported `FINIS_028` run are not present in the checked-in `data/` snapshot, so the duplicate behavior is grounded primarily in the live `build_form()` code and the Stage 2 tests rather than direct inspection of those exact output files.

## Current Live Formam Build Behavior

| Step | Live behavior on disk |
| --- | --- |
| CLI entry | `azq/cli.py` routes `form ...` to `azq/formam/router.py`, which re-exports `azq/formam/cli.py`. |
| Command dispatch | `azq/formam/cli.py` handles `azq form build <goal_id>`, calls `ensure_finis_storage_ready()`, then calls `azq.formam.build.build_form(goal_id)`. |
| Parent validation | `build_form()` calls `validate_parent_goal(goal_id, active_only=True)`, so the goal must exist in canonical Finis storage and be active. |
| Deliverable creation | `build_form()` always calls `next_deliverable_id()`, then `build_stub_deliverable_record(...)`, then `write_deliverable(...)`. |
| Stub contents | `build_stub_deliverable_record()` copies `goal_record['title']` into the deliverable `title`, uses the goal description if present, otherwise writes a fallback stub artifact description, sets `dependencies=[]`, `status='drafted'`, and `created=<today>`. |
| Map refresh | After the write, `build_form()` loads all canonical deliverables for that goal with `load_goal_deliverables(goal_id)`, loads any existing goal map, builds a map record listing the current `deliverable_ids`, forces `dependency_edges=[]`, and writes the map. |
| Operator output | `build_form()` prints `Built DELIV_### for FINIS_###`, the deliverable path, and the goal map path. |

Repo-grounded details that matter:

- `planning/stage_2/overview.md` explicitly says Stage 2 is complete when `azq form build <goal_id>` can create a stub deliverable and goal map.
- `docs/architecture/AZQ_COMMAND_MODEL.md` says live Formam “builds stub deliverables and goal maps.”
- `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md` and `planning/stage_5/deliverables.json` both describe current deliverable generation as stub-first and sparse.
- `tests/test_stage2_wave_c.py` only asserts the single-build baseline: one deliverable exists, the map lists that one deliverable, and `dependency_edges == []`.

Plainly, `azq form build` today is a canonical stub artifact writer. It is not yet a richer deliverable-shaping engine.

## Failure For This Workflow

### Is current Formam behavior stub-only or meaningfully shaping deliverables?

Stub-only.

Why that conclusion is grounded in the repo:

| Evidence | What it shows |
| --- | --- |
| `azq/formam/build.py` | The only builder is `build_stub_deliverable_record()`. |
| `build_stub_deliverable_record()` | The deliverable `title` is copied from the goal title, not shaped into a narrower artifact boundary. |
| `build_stub_deliverable_record()` | If the goal description is empty, the artifact description is a generic fallback string: `Stub deliverable for <goal_id>: define the first visible artifact boundary for <goal_title>`. |
| `azq/formam/build.py` | Only one deliverable is created per invocation. |
| `azq/formam/build.py` and `azq/formam/maps.py` | Maps are sparse and dependency-free unless deliverable records already contain dependencies. The build path itself always creates `dependencies=[]`. |
| `planning/stage_5/deliverables.json` | The current baseline is described as “single-stub baseline” and “intentionally sparse and stub-first.” |

### Why repeated `azq form build FINIS_028` can create indistinguishable duplicate deliverables

Because the build path has no rebuild guard.

Live code path:

1. `build_form(goal_id)` validates the goal.
2. It immediately calls `next_deliverable_id()`.
3. It always builds a new stub deliverable from the goal record.
4. That stub copies the same goal title each time.
5. It writes the new deliverable unconditionally.
6. It refreshes the map from all deliverables now attached to that goal.

Nothing in this path checks:

- whether that goal already has deliverables
- whether a same-title deliverable already exists for that goal
- whether the goal map already exists
- whether this is a rebuild versus a first build

So if `FINIS_028` has an empty description, repeated builds will naturally produce same-title, same-shape stub artifacts that differ mainly by `deliverable_id` and `created`. The refreshed goal map will then list both deliverables, and because each stub has `dependencies=[]`, the map will show no dependency edges.

### Is rebuild idempotent today?

No.

`build_form()` is additive, not idempotent. The use of `next_deliverable_id()` plus unconditional `write_deliverable()` guarantees a fresh canonical deliverable file whenever the command is run against a valid active goal.

### Failure classification

| Factor | Role in the bug |
| --- | --- |
| Stub generation strategy | Primary for the generic output. The current builder intentionally emits one stub deliverable with goal-title reuse and sparse description logic. |
| Missing dedupe or rebuild guard | Primary for the duplicate-build behavior. There is no idempotence check before allocating a new `DELIV_###`. |
| Missing goal-to-deliverable shaping logic | Contributing to why duplicates are indistinguishable and low-value. The system is not yet shaping a goal into distinct artifact boundaries. |

This is therefore a combination failure: stub-only generation explains the generic deliverables, and the missing rebuild guard explains the duplicate build behavior.

## Smallest Practical Fix

### Current live behavior

For every successful `azq form build <goal_id>` call:

- create one new stub deliverable
- append it to the goal’s canonical deliverables
- refresh the goal map from the resulting set

### Recommended minimal behavior

Keep the current Stage 2 stub baseline, but make rebuilds idempotent for goals that already have canonical deliverables.

| Change | Why it is the smallest useful fix |
| --- | --- |
| In `azq/formam/build.py`, check `load_goal_deliverables(goal_id)` before calling `next_deliverable_id()` | This is the narrow seam where duplicate creation currently happens. |
| If deliverables already exist for that goal, do not create a new stub deliverable; instead refresh or preserve the goal map and return the existing deliverable set | This fixes the duplicate-build failure without redesigning Formam. |
| Keep the existing stub deliverable format unchanged for the first build | This avoids broadening into Stage 5 deliverable shaping work. |

Why this is the narrowest safe fix:

- it preserves the current Stage 2 command surface
- it preserves canonical deliverable and map storage formats
- it does not add proposal artifacts, review artifacts, or richer shaping logic
- it directly addresses the observed non-idempotent rebuild failure

Conservative judgment: this fix does not solve the larger “generic stub deliverable” limitation by itself. It is still the smallest practical repair because it stops duplicate canonical artifacts from accumulating while leaving the Stage 5 shaping work for later.

## Likely File Touch Points

| File | Why it is the likely seam |
| --- | --- |
| `azq/formam/build.py` | Owns `build_form()`, `build_stub_deliverable_record()`, the unconditional `next_deliverable_id()` call, and the goal-map refresh flow. |
| `tests/test_stage2_wave_c.py` | Best place to add a narrow regression proving repeat `form build` for one goal does not create duplicate deliverables and still refreshes the map. |

Likely not needed for the first repair:

- `azq/formam/deliverable_storage.py`
- `azq/formam/maps.py`
- `azq/formam/map_storage.py`
- `azq/formam/storage.py`
- `azq/formam/schemas.py`
- `azq/formam/paths.py`

Those modules define storage and map refresh primitives, but the duplicate creation decision currently lives in `build_form()`.

## Minimum Test Surface

The minimum regression coverage should stay narrow:

| Test | What it proves |
| --- | --- |
| Running `azq form build FINIS_001` twice for the same active goal still leaves exactly one canonical deliverable for that goal | Proves rebuild is idempotent. |
| The second build still leaves a canonical goal map present and linked to that goal | Proves the idempotence guard does not break map refresh behavior. |
| The first build still creates one canonical stub deliverable and one canonical goal map | Proves the Stage 2 baseline still works. |
| Existing `tests/test_stage2_wave_c.py` flow still passes | Proves no regression to list/show/map baseline behavior. |

If one extra assertion is desired, it should confirm that the existing deliverable id is preserved on rebuild rather than replaced.

## Recommended Next Step

Implement one narrow idempotence guard in `azq/formam/build.py`:

1. Validate the parent goal as today.
2. Load canonical deliverables for that goal before allocating a new id.
3. If at least one deliverable already exists, skip new deliverable creation.
4. Refresh the canonical goal map from the existing deliverable set and return that result.
5. Only allocate `next_deliverable_id()` and write a stub deliverable when the goal has no deliverables yet.

That is the narrowest safe next implementation step because it fixes the duplicate-build failure immediately without pretending current Formam already does meaningful multi-deliverable shaping.

## Closing Summary

`azq form build` today is a thin Stage 2 baseline command. It validates one active goal, creates one new stub deliverable whose title is copied from the goal title, writes it canonically, then refreshes a sparse goal map from all deliverables attached to that goal.

Current Formam is therefore stub-only, not yet meaningfully shaping deliverables. Rebuild is not idempotent today because `build_form()` always allocates a fresh `DELIV_###` and never checks whether that goal has already been built. The smallest practical fix is to keep the stub baseline and add an idempotence guard in `azq/formam/build.py` so repeat builds reuse the existing deliverable set and refresh the map instead of creating duplicate canonical deliverables.
