# AZQ Architecture Repair Task List

## Executive Summary

This artifact converts `codex/reports/azq_medulla_alignment_report.md` into a small, ordered document-repair list for the current repo.

It is grounded in `docs/architecture/AZQ_Medulla.md`, the live repo under `azq/`, the checked-in `data/` tree, the Stage 1 to Stage 3 planning and test baseline under `planning/` and `tests/`, and the current architecture docs under `docs/architecture/`.

The repair wave should start with the documents that can mislead future Opifex / Codex work into building against false canonical state. That means `docs/architecture/AZQ_STATE_MODEL.md` first, then the thinner doctrinal documents that weaken Medulla protection without being fully wrong, then the small corrections needed in otherwise strong docs.

The strongest aligned docs should be preserved. This is a repair wave, not a rewrite-everything wave.

## Repair Task Ordering Principles

- Start with the documents that teach false live reality, not the documents that are merely broad or poetic.
- Treat `docs/architecture/AZQ_Medulla.md` as the doctrinal authority when documents disagree.
- Prefer `revise` when a document is materially misleading.
- Prefer `tighten`, `harmonize`, or `narrow` when a document is still useful but claims too much or protects too little.
- Preserve the strongest repo-truth documents with only small corrections.
- Keep every task document-scoped and reviewable.
- Keep this wave focused on architecture-document safety, not engine-feature planning.

## Priority 1 Repair Tasks

1. `DOC_REPAIR_001`
Target file: `docs/architecture/AZQ_STATE_MODEL.md`
Repair action: `revise`
Why this matters: the Medulla alignment report identifies this as the highest-risk document because it teaches stale Finis storage, non-live commands, and state transitions the repo does not currently enforce. That makes it unsafe as a build authority for future Opifex work.
Definition of done: the file no longer claims `data/finis/goals.json` is current canonical storage, no longer teaches non-live command families such as `azq goal create`, `azq goal pause`, `azq goal resume`, `azq archive`, `azq prune`, `azq task complete`, `azq status`, or `azq doctor` as current behavior, and clearly separates live state grammar from future direction in a way that matches `azq/cli.py`, `azq/finis/storage.py`, `azq/agenda/build.py`, and the Stage 1 to Stage 3 tests.

2. `DOC_REPAIR_002`
Target file: `docs/architecture/AZQ_CRAFT_CHARTER.md`
Repair action: `tighten`
Why this matters: the charter is structurally sound, but the current wording around deletion and pruning is weak against the Medulla's continuity and archive-first standard. If left as-is, it can justify anti-Medulla cleanup behavior.
Definition of done: the charter still preserves the five-engine craft order and deliverables-before-tasks law, but its craft laws now clearly subordinate deletion to continuity and stewardship, and the document explicitly protects lineage, accepted canonical state, and the human-vs-model judgment boundary in Medulla terms.

3. `DOC_REPAIR_003`
Target file: `docs/architecture/AZQ_PLANNING_LOOP.md`
Repair action: `narrow`
Why this matters: the planning loop is useful, but the alignment report found that it can pull the architecture layer toward a generic visible-planning system instead of the AZQ craft spine. That is a doctrine risk before it becomes a feature risk.
Definition of done: the document remains alive, but it explicitly states that planning-loop artifacts are subordinate to `spark -> goal -> deliverable -> task -> action -> stewardship`, are not a separate public engine, and must not blur proposal artifacts with accepted canonical state.

## Priority 2 Repair Tasks

1. `DOC_REPAIR_004`
Target file: `docs/architecture/AZQ_Manifesto.md`
Repair action: `trim`
Why this matters: the manifesto is not anti-Medulla, but it is more poetic than build-safe. The alignment report found that it does not protect lineage, continuity, and accepted-state boundaries strongly enough for implementation work.
Definition of done: the manifesto keeps its anti-task-manager and human-first tone, but is reduced enough that it no longer reads like a broad parallel doctrine path competing with Medulla, the implementation plan, and the engine/command/filesystem set.

2. `DOC_REPAIR_005`
Target file: `docs/architecture/AZQ_Manifesto.md` and `docs/architecture/AZQ_PHILOSOPHY.md`
Repair action: `harmonize`
Why this matters: both documents are still useful, but the philosophy is sharper than the manifesto on proposal-vs-accepted state and machine-shaped suggestions. They should agree instead of teaching two different levels of doctrinal precision.
Definition of done: the two documents agree on the human-first role of AZQ, the proposal-versus-accepted distinction, and the warning against generic task-manager drift, without duplicating the stronger repo-truth role already carried by the implementation, engine, command, and filesystem docs.

3. `DOC_REPAIR_006`
Target file: `docs/architecture/AZQ_PHILOSOPHY.md`
Repair action: `tighten`
Why this matters: the philosophy is doctrinally useful, but it still needs a tighter link to live repo consequences so future work does not treat it as pure abstraction.
Definition of done: the document keeps its current strengths, but includes a clearer bridge from doctrine to the current accepted-state seams under `data/finis/goals/`, `data/form/`, and `data/agenda/`, while staying within the current repo truth that proposal families are mostly future-facing.

## Priority 3 Cleanup Tasks

1. `DOC_REPAIR_007`
Target file: `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md`
Repair action: `clarify`
Why this matters: this is one of the strongest docs and should be preserved. The only notable issue from the alignment report is that task-log language can read stronger than the current live flow, since `azq/agenda/build.py` does not create logs and checked-in `data/agenda/logs/` is empty.
Definition of done: the document still stands as a strong baseline authority, but its Stage 3 wording makes clear that task-log storage exists while live task-build integration remains limited.

2. `DOC_REPAIR_008`
Target file: `docs/architecture/AZQ_ENGINE_SPEC.md`
Repair action: `clarify`
Why this matters: this is another strong Medulla servant and should not be rewritten. It only needs a small correction so the live Agenda baseline is not overstated.
Definition of done: the document still defines engine boundaries and proposal-vs-canonical rules, but its Agenda section makes clear that task-log helpers exist without implying that logs are already part of the main live task-build path.

3. `DOC_REPAIR_009`
Target file: `docs/architecture/AZQ_COMMAND_MODEL.md`, `docs/architecture/AZQ_FILESYSTEM_MODEL.md`, `docs/architecture/AZQ_BOOTSTRAP.md`, and `README.md`
Repair action: `harmonize`
Why this matters: these are strong docs that mostly agree with repo truth. The repair needed here is narrow: keep the live baseline consistent about task logs and avoid teaching stronger live behavior than `azq/agenda/build.py` and the empty checked-in `data/agenda/` tree support.
Definition of done: these documents still preserve the current command surface and artifact homes, but they now agree on the same narrow statement that `data/agenda/logs/` is a canonical storage home with helper support, not yet a routine output of the main live build path.

4. `DOC_REPAIR_010`
Target file: `pyproject.toml`
Repair action: `update metadata`
Why this matters: this is low doctrinal risk, but it weakens continuity between package identity and the actual repo baseline by describing AZQ as if it were still Scintilla-first only.
Definition of done: the package description reflects the current Stage 3-capable AZQ baseline without pretending Domum or deeper LLM shaping is already live.

## Suggested Human Review Checkpoints

- After Priority 1: stop for human review before any further Opifex feature work. This is the main build-safety checkpoint because it fixes the document that can actively mislead implementation.
- After Priority 2: stop for human review before touching the stronger docs. This confirms that the doctrinal layer now points cleanly back to Medulla instead of competing with it.
- After Priority 3: final review for consistency across the architecture set, with special attention to whether the strongest docs were preserved rather than broadened.

## Proposed Repair Sequence Summary

1. `DOC_REPAIR_001` on `docs/architecture/AZQ_STATE_MODEL.md`
2. `DOC_REPAIR_002` on `docs/architecture/AZQ_CRAFT_CHARTER.md`
3. `DOC_REPAIR_003` on `docs/architecture/AZQ_PLANNING_LOOP.md`
4. Human review checkpoint
5. `DOC_REPAIR_004` on `docs/architecture/AZQ_Manifesto.md`
6. `DOC_REPAIR_005` across `docs/architecture/AZQ_Manifesto.md` and `docs/architecture/AZQ_PHILOSOPHY.md`
7. `DOC_REPAIR_006` on `docs/architecture/AZQ_PHILOSOPHY.md`
8. Human review checkpoint
9. `DOC_REPAIR_007` on `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md`
10. `DOC_REPAIR_008` on `docs/architecture/AZQ_ENGINE_SPEC.md`
11. `DOC_REPAIR_009` across `docs/architecture/AZQ_COMMAND_MODEL.md`, `docs/architecture/AZQ_FILESYSTEM_MODEL.md`, `docs/architecture/AZQ_BOOTSTRAP.md`, and `README.md`
12. `DOC_REPAIR_010` on `pyproject.toml`
13. Final consistency review

This ordering follows the Medulla alignment report's urgency, with one small conservative adjustment: the task-log overstatement issue remains Priority 3 because the report treats it as a narrow correction inside otherwise strong docs, not as a reason to reopen the whole architecture layer.

## Closing Summary

This task list is a doctrine-repair wave, not a feature roadmap. It is designed to reduce build risk for future Codex / Opifex work by correcting the documents most likely to distort human intent, lineage, continuity, and accepted canonical state.

The highest priority repairs are `docs/architecture/AZQ_STATE_MODEL.md`, `docs/architecture/AZQ_CRAFT_CHARTER.md`, and `docs/architecture/AZQ_PLANNING_LOOP.md`. The docs that should be preserved with only small corrections are `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md`, `docs/architecture/AZQ_ENGINE_SPEC.md`, `docs/architecture/AZQ_COMMAND_MODEL.md`, `docs/architecture/AZQ_FILESYSTEM_MODEL.md`, `docs/architecture/AZQ_BOOTSTRAP.md`, and `README.md`.

Some tasks remain conservative by design, especially where the repo has future-facing proposal or stewardship ideas without live artifact families yet. That is intentional. The list is meant to be safe for Opifex to execute one task at a time without drifting into engine-feature work.
