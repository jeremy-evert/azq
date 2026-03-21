# AZQ Finis Candidate Dedupe Failure Report

## Executive Summary

`azq fine` currently filters candidate goals before they reach Finis review. In live code, `azq/finis/fine.py` cleans each spark into a short title, lowercases it, compares it against every existing canonical goal title with `difflib.SequenceMatcher`, and drops the candidate if any score is at or above `TITLE_DEDUPE_THRESHOLD = 0.39`.

For the `2026-03-20_121334` spark file, that duplicate gate rejects both new candidates before `write_candidate_reviews()` runs, which is why the new spark produces zero reviewable candidates even though Finis review artifacts now exist. The failure is mainly a combination of weak comparison strategy, low threshold for this corpus, and noisy legacy goal titles. The smallest practical fix is to keep the current flow, but make duplicate rejection materially stricter by comparing normalized titles on both sides and raising the duplicate threshold enough that unrelated titles like `FINIS_020` and `FINIS_022` no longer block review.

Conservative judgment: a threshold increase alone would likely unblock this exact spark, but the repo evidence suggests the safer minimal repair is threshold adjustment plus symmetric title normalization, not a larger redesign.

## Current Live Candidate Dedupe Behavior

| Step | Live behavior on disk |
| --- | --- |
| Spark load | `load_sparks()` reads every `*.json` file under `data/scintilla/sparks/` and emits `spark`, `source`, and `spark_index`. |
| Source skip | `get_used_sources()` collects every value in canonical goals' `derived_from`; `propose_goals()` skips any spark whose `source` already appears there. |
| Candidate cleanup | `clean_goal_text()` strips a small prefix list, normalizes whitespace, and capitalizes the first character. |
| Duplicate check | `propose_goals()` loads canonical goals through `storage.load_all_goals(migrate_legacy=True)`, lowercases each goal `title`, and rejects a candidate when `SequenceMatcher(...).ratio() >= 0.39` against any existing title. |
| Review write | Only non-duplicate candidates are written by `write_candidate_reviews()` into `data/finis/reviews/<review_id>.json`. |
| Promotion | Accepted reviews become canonical goal files through `promote_accepted_reviews()`, which writes `data/finis/goals/FINIS_###.md` and updates the review with `review_status=accepted` and `accepted_goal_id`. |

Two live details matter for this bug:

1. Duplicate filtering happens before Finis review artifacts are written.
2. The comparison uses short cleaned candidate text against the current checked-in goal title corpus, which includes many conversational, weakly normalized, or low-signal titles such as `FINIS_020`, `FINIS_022`, `FINIS_019`, `FINIS_018`, `FINIS_003`, `FINIS_015`, and `FINIS_026`.

## Failure For This Workflow

The failing spark file on disk is `data/scintilla/sparks/2026-03-20_121334.json`. It contains:

- `we need to fix azq to make the alignment match better`
- `the docs do not all agree, and we need a usable spark ingress path`

Under current live code, both become cleaned candidate titles and are then rejected by the duplicate gate before review files are written.

| Candidate | Live top match | Score | Why this is a false positive |
| --- | --- | ---: | --- |
| `We need to fix azq to make the alignment match better` | `FINIS_022` `It's small, but it makes the system dramatically more durable` | 0.421 | The existing title is vague durability language, not alignment matching work. |
| same | `FINIS_020` `They recommended a 15 line guard rail that prevents corrupted goals` | 0.383 | Close score, but still unrelated in intent. |
| `The docs do not all agree, and we need a usable spark ingress path` | `FINIS_020` | 0.406 | Corrupted-goal guard rails are not spark ingress. |
| same | `FINIS_025` `add azq goals --all to show all active, completed, and archived goals.` | 0.382 | CLI goal listing is not spark ingress. |
| same | `FINIS_010` `Stabilize the Scintilla and Finis engines of AZQ` | 0.351 | Broad engine stabilization is not the same as docs alignment and ingress repair. |

Why the current behavior is insufficient:

- The duplicate gate is catching broad wording overlap, not duplicate intent.
- Existing goal titles are not a clean comparison corpus. Several checked-in goals are conversational, malformed, or modelish rather than stable short titles.
- `clean_goal_text()` is applied only to the incoming candidate. Existing canonical titles are compared mostly as-is, so the dedupe check is asymmetric.
- The current threshold is too low for this corpus. Scores around `0.40` are demonstrably high enough to suppress unrelated new work.

Failure classification:

| Factor | Role in the bug |
| --- | --- |
| Comparison strategy | Primary. Raw character-level `SequenceMatcher` on short titles is too weak a proxy for duplicate intent. |
| Threshold tuning | Primary. `0.39` is low enough to reject clearly distinct work in the current goal corpus. |
| Title normalization | Contributing. The incoming side is cleaned, but stored titles are not normalized to the same standard before comparison. |
| Legacy goal quality | Contributing. The checked-in goal store contains many titles that are poor dedupe anchors. |

This is therefore a combination failure, with comparison strategy and threshold doing most of the damage.

## Smallest Practical Fix

### Current live behavior

Reject a candidate if its lowercased cleaned title has `SequenceMatcher` similarity `>= 0.39` against any lowercased canonical goal title.

### Recommended minimal behavior

Keep the current Finis flow and source-based skip rule, but tighten duplicate rejection as follows:

| Change | Why it is the smallest useful fix |
| --- | --- |
| Normalize existing goal titles with the same `clean_goal_text()` logic before similarity comparison | Removes the current asymmetry without redesigning storage. |
| Raise the duplicate threshold materially above the current `0.39` | Prevents obviously distinct candidates from being dropped before review. |

Why this is the narrowest safe fix:

- It keeps duplicate filtering in `azq/finis/fine.py`.
- It does not require a new engine, new artifact type, or a Finis redesign.
- It does not require cleanup of all historical goals before the repair can ship.
- It directly targets the pre-review false-positive gate that caused zero candidates here.

Conservative judgment: the exact replacement threshold should be chosen with a small regression test around this live failure. Repo evidence supports that it must be high enough to let the two `2026-03-20_121334` candidates survive review creation.

## Likely File Touch Points

| File | Why it is the likely seam |
| --- | --- |
| `azq/finis/fine.py` | Owns `TITLE_DEDUPE_THRESHOLD`, `clean_goal_text()`, `similar()`, and the duplicate gate inside `propose_goals()`. |
| `tests/test_stage4_wave_a.py` | Best place to add a regression for review creation surviving false-positive dedupe. |
| `tests/test_stage1_wave_c.py` | Holds the existing `azq fine` canonical-goal baseline and may need a small assertion adjustment only if shared helper behavior changes. |

Likely not needed for the first repair:

- `azq/finis/storage.py`
- `azq/finis/goals.py`

Those files are not where the false-positive dedupe decision is made.

## Minimum Test Surface

The minimum regression coverage should stay narrow:

| Test | What it proves |
| --- | --- |
| A spark file containing the two `2026-03-20_121334` candidates produces review artifacts instead of `No candidate goals to review.` when the checked-in goal titles are present as dedupe inputs | Proves this exact false-positive failure is fixed. |
| A clearly duplicated candidate still gets filtered | Proves the dedupe gate still exists after the threshold and normalization change. |
| Accepting a surviving candidate still promotes it into a canonical `FINIS_###.md` goal with `derived_from` and updates the review record | Proves the repair does not break the existing review-to-goal path. |

## Recommended Next Step

Implement the smallest code change in `azq/finis/fine.py`:

1. Normalize existing goal titles with the same cleanup path used for candidate titles.
2. Raise the title dedupe threshold to a materially stricter value.
3. Add one regression in `tests/test_stage4_wave_a.py` for the `2026-03-20_121334` false-positive case.

That is the narrowest safe next implementation step because it repairs the live pre-review rejection without broadening Finis beyond candidate dedupe.

## Closing Summary

Today, `azq fine` loads sparks, skips already-derived sources, cleans each spark into a candidate title, and rejects that candidate before review if any existing goal title reaches `SequenceMatcher` similarity `>= 0.39`. In the current goal corpus, that causes unrelated titles such as `FINIS_020` and `FINIS_022` to block legitimate new candidates from `2026-03-20_121334`.

The failure is not mainly that Finis lacks a review seam. The review seam exists in live code, but the candidate never reaches it. The smallest practical fix is to keep the current flow and make duplicate rejection stricter by normalizing both sides of the title comparison and raising the threshold enough to stop broad wording overlap from suppressing reviewable new work.
