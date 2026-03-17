# AZQ Command Model

## Purpose

This document proposes the command set needed to execute AZQ's stated goals across all five engines:

`spark -> goal -> deliverable -> task -> artifact -> archive`

It combines:

- commands already implemented in the current CLI
- commands required by the spec but not yet implemented
- shell commands needed to bootstrap and operate the repository

---

## Command Design Rules

- Keep commands short, memorable, and stage-specific.
- Preserve stage boundaries: no task commands before form commands.
- Favor inspectable file outputs in `data/`.
- Every command should map to a durable artifact or explicit state change.

---

## 1. Bootstrap And Environment Commands

Use these to initialize a repository consistent with the filesystem model.

```bash
# create required directories
mkdir -p \
  data/scintilla/audio data/scintilla/transcripts data/scintilla/sparks \
  data/finis/goals data/finis/reviews \
  data/form/deliverables data/form/maps \
  data/agenda/tasks data/agenda/dags data/agenda/logs \
  data/artifacts/code data/artifacts/notes data/artifacts/docs data/artifacts/modules \
  data/archive/goals data/archive/tasks data/archive/sparks data/archive/artifacts \
  logs scripts tests

# install package in editable mode
pip install -e .

# show available CLI commands
azq
```

---

## 2. Canonical CLI Surface

Top-level layout:

```text
azq <engine|resource> <verb> [args]
```

Shared utility commands:

```bash
azq status           # pipeline snapshot across stages
azq doctor           # validate directories/filesystem health
azq review           # daily/weekly summary
azq version
```

---

## 3. Engine Commands

### Cole Scintilla (Gather Sparks)

Implemented now:

```bash
azq capture
azq sparks
azq spark <id>
azq spark search <text>
azq spark rm <id>
```

Suggested additions:

```bash
azq capture text "<note>"
azq capture import <file>
azq spark tag <id> <tag>
azq spark link <spark_id> <goal_id>
```

### Respice Finem (Consider The End)

Implemented now:

```bash
azq fine
azq goals
azq goal add
azq goal close <id>
azq goal archive <id>
```

Spec-aligned aliases/additions:

```bash
azq goals review
azq goal create
azq goal show <id>
azq goal link-sparks <goal_id> <spark_ids...>
azq goal reopen <id>
```

### Strue Formam (Build The Form)

Needed for full spec:

```bash
azq form build <goal_id>
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
azq form validate <deliverable_id>
```

### Age Agenda (Drive The Work)

Needed for full spec:

```bash
azq agenda
azq task list
azq task show <task_id>
azq task start <task_id>
azq task complete <task_id>
azq task block <task_id> "<reason>"
azq dag build <goal_id>
azq dag show <goal_id>
```

### Custodi Domum (Keep The House)

Needed for full spec:

```bash
azq archive
azq archive goal <goal_id>
azq archive task <task_id>
azq prune
azq prune sparks --older-than <days>
azq review
azq report health
```

---

## 4. Scripts And Operational Commands

Scripts identified in the filesystem model should be callable directly and through CLI wrappers.

```bash
python scripts/daily_review.py
python scripts/archive_cleanup.py
python scripts/goal_report.py
```

Wrapper equivalents:

```bash
azq review daily
azq archive cleanup
azq report goals
```

---

## 5. Test And Quality Commands

```bash
pytest -q
pytest tests/test_scintilla.py -q
pytest tests/test_finis.py -q
pytest tests/test_formam.py -q
```

Optional checks:

```bash
python -m pip check
python -m compileall azq
```

---

## 6. Recommended End-To-End Daily Flow

```bash
# 1) gather
azq capture
azq sparks

# 2) choose ends
azq fine
azq goals review

# 3) shape work
azq form build FINIS_001
azq form list

# 4) execute
azq dag build FINIS_001
azq task list
azq task start TASK_001
azq task complete TASK_001

# 5) maintain
azq review
azq archive
azq prune
```

---

## 7. Implementation Priority (Command Backlog)

1. Add `azq status` and `azq doctor` for observability.
2. Implement `form` command group (`build/list/show`).
3. Implement `task` and `dag` command groups.
4. Implement `archive/prune/report` command group.
5. Add aliases so implemented Finis commands match engine spec (`goal create`, `goals review`).

This priority preserves the charter rule: shape before tasks, tasks before maintenance.
