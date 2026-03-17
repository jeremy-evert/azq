# AZQ State Model

## Purpose

This document defines the formal state model of AZQ.

It is the lifecycle grammar of the system: how work exists, how it moves, what commands are allowed to change it, and what evidence on disk proves that a transition actually occurred.

The state model exists to keep five things true:

1. The craft stages remain distinct.
2. The filesystem remains the visible source of truth.
3. Every meaningful transition is inspectable.
4. The CLI remains small and memorable.
5. No command can claim success without leaving durable evidence.

AZQ is not a bag of commands.
It is a staged craft system.
Its state model therefore expresses the Rule of Craft:

```text
seed -> intention -> form -> labor -> stewardship
```

In AZQ terms:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
```

---

## Governing Relationship To Other Documents

This document depends on the other architectural documents and should be read after them.

* `AZQ_CRAFT_CHARTER.md` defines the craft stages and laws.
* `AZQ_ENGINE_SPEC.md` defines the operational responsibilities of each engine.
* `AZQ_FILESYSTEM_MODEL.md` defines where artifacts live on disk.
* `AZQ_COMMAND_MODEL.md` defines the CLI surface.

This document adds the missing layer:

* object states
* legal transitions
* command run states
* repository maturity states
* repository health states
* invariants that must remain true during implementation

---

## First Principle

AZQ has four different kinds of state.

These must not be confused.

### 1. Object State

The state of a specific thing being worked on.

Examples:

* a spark is reviewable
* a goal is active
* a deliverable is approved
* a task is blocked
* an artifact is archived

### 2. Command State

The state of a command while it is running.

Examples:

* invoked
* validated
* executing
* committed
* failed

### 3. Repository State

The visible maturity of the repository as a whole.

Examples:

* empty
* seeded
* purposed
* formed
* actionable
* realized
* kept

### 4. Health State

The quality condition of the system.

Examples:

* healthy
* warning
* degraded
* inconsistent

Object state is primary.
Command state exists to change object state.
Repository state is the aggregate result.
Health state describes whether the system can be trusted.

---

## Canonical Pipeline

The formal AZQ lifecycle is:

```text
observation
  -> captured input
  -> transcript or text note
  -> spark record
  -> goal
  -> deliverable
  -> dependency map
  -> task
  -> work log
  -> artifact
  -> archive
```

The filesystem should mirror this directly:

```text
data/scintilla/
  audio/
  transcripts/
  sparks/

data/finis/
  goals/
  reviews/

data/form/
  deliverables/
  maps/

data/agenda/
  tasks/
  dags/
  logs/

data/artifacts/
data/archive/
```

No hidden database state should be required to understand where work stands.

---

## Repository Maturity States

The repository as a whole can be described by the farthest populated stage that is still active.

### `empty`

No craft artifacts exist yet.

### `seeded`

At least one spark exists, but no active goal exists yet.

### `purposed`

At least one active goal exists, but no deliverable exists for that goal.

### `formed`

At least one deliverable exists, but no executable task exists yet.

### `actionable`

At least one open task exists.

### `realized`

At least one artifact exists in `data/artifacts/`.

### `kept`

At least one object has been archived or a maintenance report has been produced.

These are not mutually exclusive historical categories.
They describe the highest visible maturity of current work.

---

## Repository Health States

Repository maturity is not the same as repository health.

### `healthy`

All required directories exist.
Required backlinks resolve.
No corrupted active files are known.

### `warning`

The system is usable but something needs attention.

Examples:

* stale active goals
* orphan sparks
* archived work backlog
* missing review reports

### `degraded`

The system still functions but normal workflow is impaired.

Examples:

* missing required directories
* missing task logs for in-progress tasks
* goal records without readable status

### `inconsistent`

The visible artifacts contradict the state model.

Examples:

* task exists without deliverable parent
* deliverable exists without goal parent
* archived object still listed as active

`azq doctor` should eventually classify the repository into one of these health states.

---

## Lifecycle Bands

AZQ work moves through six top-level lifecycle bands.

| Lifecycle Band | Craft Stage      | Primary Object  | Filesystem Home   |
| -------------- | ---------------- | --------------- | ----------------- |
| `seeded`       | Cole Scintilla   | spark           | `data/scintilla/` |
| `purposed`     | Respice Finem    | goal            | `data/finis/`     |
| `formed`       | Strue Formam     | deliverable/map | `data/form/`      |
| `actionable`   | Age Agenda       | task/dag/log    | `data/agenda/`    |
| `realized`     | artifact outcome | artifact        | `data/artifacts/` |
| `kept`         | Custodi Domum    | archive/report  | `data/archive/`   |

These lifecycle bands are teaching terms and summary terms.
They do not replace the engine-specific states below.

---

## Engine 1: Cole Scintilla

Cole Scintilla governs the transition from fleeting observation to durable spark.

### Spark Object States

1. `not_captured`
2. `captured_audio`
3. `captured_text`
4. `transcribed`
5. `extracted`
6. `reviewable`
7. `linked`
8. `archived`
9. `pruned`

### State Definitions

#### `not_captured`

The idea exists only in the world or in memory.

#### `captured_audio`

An audio file exists:

```text
data/scintilla/audio/<id>.wav
```

#### `captured_text`

A direct text capture exists and is ready to become or already is a spark.

#### `transcribed`

A transcript exists:

```text
data/scintilla/transcripts/<id>.txt
```

#### `extracted`

A spark record exists:

```text
data/scintilla/sparks/<id>.json
```

This is the first canonical pipeline state.

#### `reviewable`

The spark is live, readable, and not yet linked to a goal.

#### `linked`

The spark is referenced by one or more goals.

#### `archived`

The spark is preserved in archive and removed from active circulation.

#### `pruned`

The spark was intentionally removed under explicit policy.

### Spark Transitions

| From             | To               | Trigger                                     | Durable Evidence                |
| ---------------- | ---------------- | ------------------------------------------- | ------------------------------- |
| `not_captured`   | `captured_audio` | `azq capture`                               | `.wav` file                     |
| `not_captured`   | `captured_text`  | `azq capture text`                          | text note or spark draft        |
| `captured_audio` | `transcribed`    | transcription succeeds                      | `.txt` file                     |
| `captured_text`  | `extracted`      | spark record written                        | `.json` file                    |
| `transcribed`    | `extracted`      | extraction succeeds                         | `.json` file                    |
| `extracted`      | `reviewable`     | write committed cleanly                     | spark visible in list           |
| `reviewable`     | `linked`         | `azq goal create` or `azq goal link-sparks` | backlink in goal record         |
| `reviewable`     | `archived`       | `azq archive`                               | object moved or marked archived |
| `reviewable`     | `pruned`         | `azq prune`                                 | explicit prune record           |
| `linked`         | `archived`       | `azq archive spark <id>`                    | object moved or marked archived |

### Spark Invariants

* A spoken spark is not fully captured unless a spark record exists.
* Transcript failure must not erase audio.
* Extraction failure must not erase transcript.
* A linked spark must remain traceable to its source transcript or text capture.
* Archive is preferred over prune.

### Current Implementation Note

The current code implements audio capture, transcription, extraction, spark listing, spark inspection, spark search, and direct spark deletion. A first-class text capture command is part of the command model but is not yet implemented in code.

---

## Engine 2: Respice Finem

Respice Finem governs the transition from sparks to goals.

### Goal Object States

1. `proposed`
2. `active`
3. `paused`
4. `completed`
5. `archived`
6. `superseded`

### State Definitions

#### `proposed`

A candidate goal exists but has not yet been accepted into active work.

#### `active`

The goal has been accepted as worthy of pursuit.

#### `paused`

The goal remains valid but is intentionally not advancing.

#### `completed`

The goal’s intended outcome has been materially achieved.

#### `archived`

The goal is preserved but no longer active.

#### `superseded`

The goal has been replaced by a clearer or narrower goal while preserving provenance.

### Goal Transitions

| From               | To           | Trigger                       | Durable Evidence                 |
| ------------------ | ------------ | ----------------------------- | -------------------------------- |
| `reviewable spark` | `proposed`   | `azq fine`                    | proposal record or candidate set |
| `proposed`         | `active`     | `azq goal create`             | goal record                      |
| `active`           | `paused`     | `azq goal pause <id>`         | status update                    |
| `paused`           | `active`     | `azq goal resume <id>`        | status update                    |
| `active`           | `completed`  | `azq goal close <id>`         | status update                    |
| `active`           | `archived`   | `azq goal archive <id>`       | archive marker or move           |
| `paused`           | `archived`   | `azq goal archive <id>`       | archive marker or move           |
| `active`           | `superseded` | split or replacement accepted | supersession backlink            |
| `completed`        | `archived`   | `azq archive goal <id>`       | archive move                     |

### Goal Invariants

* Every active goal should point toward an artifact or visible change.
* Every goal should preserve backlinks to originating sparks.
* Goal state must be inspectable as plain files.
* Closing a goal must not destroy provenance.

### Current Implementation Note

The current repository still uses `data/finis/goals.json` rather than fully normalized goal files. That is a real implementation gap between the filesystem model and the current code.

---

## Engine 3: Strue Formam

Strue Formam governs the transition from purpose to structure.

### Deliverable Object States

1. `unformed`
2. `drafted`
3. `mapped`
4. `approved`
5. `superseded`
6. `archived`

### State Definitions

#### `unformed`

A goal exists but no deliverable exists yet.

#### `drafted`

At least one deliverable file has been written.

#### `mapped`

A dependency or structure map exists.

#### `approved`

The form is stable enough to be translated into tasks.

#### `superseded`

The deliverable definition has been replaced while preserving history.

#### `archived`

The deliverable is preserved but no longer active.

### Deliverable Transitions

| From          | To           | Trigger                          | Durable Evidence  |
| ------------- | ------------ | -------------------------------- | ----------------- |
| `active goal` | `unformed`   | goal exists with no deliverables | none yet          |
| `unformed`    | `drafted`    | `azq form build <goal_id>`       | deliverable file  |
| `drafted`     | `mapped`     | `azq form map <goal_id>`         | map file          |
| `mapped`      | `approved`   | user accepts structure           | approval marker   |
| `drafted`     | `superseded` | revision replaces prior form     | revision backlink |
| `approved`    | `archived`   | `azq archive`                    | archive move      |

### Formam Invariants

* Deliverables describe artifacts, not errands.
* Tasks may not exist without at least one approved deliverable.
* A goal may own multiple deliverables.
* Maps must make dependencies visible.

---

## Engine 4: Age Agenda

Age Agenda governs the transition from structure to executable work.

### Task Object States

1. `unplanned`
2. `ready`
3. `in_progress`
4. `blocked`
5. `completed`
6. `canceled`
7. `archived`

### State Definitions

#### `unplanned`

The deliverable exists but no actionable task has been created yet.

#### `ready`

The task exists and is available for execution.

#### `in_progress`

Work has started and a work log should exist.

#### `blocked`

Execution cannot continue.

#### `completed`

The task’s expected work has finished.

#### `canceled`

The task was intentionally abandoned.

#### `archived`

The task is preserved as history.

### Task Transitions

| From                   | To            | Trigger                                    | Durable Evidence                 |
| ---------------------- | ------------- | ------------------------------------------ | -------------------------------- |
| `approved deliverable` | `unplanned`   | deliverable enters agenda scope            | none yet                         |
| `unplanned`            | `ready`       | `azq dag build <goal_id>` or task creation | task file and dag                |
| `ready`                | `in_progress` | `azq task start <task_id>`                 | work log opened                  |
| `in_progress`          | `blocked`     | `azq task block <task_id>`                 | block reason logged              |
| `blocked`              | `ready`       | `azq task unblock <task_id>`               | unblock event logged             |
| `in_progress`          | `completed`   | `azq task complete <task_id>`              | status update and completion log |
| `ready`                | `canceled`    | `azq task cancel <task_id>`                | status update                    |
| `blocked`              | `canceled`    | `azq task cancel <task_id>`                | status update                    |
| `completed`            | `archived`    | `azq archive task <task_id>`               | archive move                     |
| `canceled`             | `archived`    | `azq archive task <task_id>`               | archive move                     |

### Agenda Invariants

* Every task must derive from a deliverable.
* A task should have one clear completion condition.
* In-progress work should create visible logs.
* Blocked work must be representable as a first-class state.

---

## Engine 5: Custodi Domum

Custodi Domum governs stewardship.

### Stewardship States

1. `live`
2. `stale`
3. `reviewed`
4. `archived`
5. `pruned`

### State Definitions

#### `live`

The record is in active circulation.

#### `stale`

The record has seen no meaningful progress for a review interval.

#### `reviewed`

A human has explicitly examined the record and decided its next status.

#### `archived`

The record is preserved for history.

#### `pruned`

The record has been intentionally removed under explicit policy.

### Stewardship Transitions

| From        | To         | Trigger              | Durable Evidence        |
| ----------- | ---------- | -------------------- | ----------------------- |
| `live`      | `stale`    | review window passes | review candidate flag   |
| `stale`     | `reviewed` | `azq review`         | maintenance report      |
| `reviewed`  | `live`     | user recommits work  | renewed activity marker |
| `reviewed`  | `archived` | `azq archive`        | archive move            |
| `reviewed`  | `pruned`   | `azq prune`          | prune record            |
| `completed` | `archived` | `azq archive`        | archive move            |

### Domum Invariants

* Nothing important should disappear silently.
* Archive is safer than prune.
* Review should precede prune whenever possible.
* Maintenance should preserve discoverability.

---

## Artifact Realization State

Artifacts are first-class objects, not merely outcomes.

### Artifact Object States

1. `planned`
2. `produced`
3. `verified`
4. `published`
5. `archived`

### State Definitions

#### `planned`

The artifact is implied by deliverables or tasks but does not yet exist.

#### `produced`

A file or module exists in `data/artifacts/`.

#### `verified`

The artifact has been reviewed, tested, or otherwise validated.

#### `published`

The artifact is considered an accepted output of the system.

#### `archived`

The artifact has been moved to historical storage.

### Artifact Transitions

| From        | To          | Trigger                       | Durable Evidence   |
| ----------- | ----------- | ----------------------------- | ------------------ |
| `planned`   | `produced`  | task completion writes output | artifact file      |
| `produced`  | `verified`  | review, test, or acceptance   | verification note  |
| `verified`  | `published` | explicit acceptance           | publication marker |
| `published` | `archived`  | `azq archive`                 | archive move       |

### Artifact Invariants

* Every artifact should backlink to task ids and deliverable id.
* Artifacts must live in plain files or plain directories.
* An artifact should not be considered published without evidence.

---

## Command Run State Model

Every AZQ command run should move through a common runtime sequence.

### Command States

1. `invoked`
2. `resolved`
3. `validated`
4. `executing`
5. `staged`
6. `committed`
7. `reported`
8. `failed`
9. `aborted`

### State Definitions

#### `invoked`

The user has run an `azq` command.

#### `resolved`

The CLI has identified which engine and verb should handle the request.

#### `validated`

Arguments, required files, and legal preconditions are checked.

#### `executing`

The command is actively performing the transition.

#### `staged`

Outputs exist in temporary or pre-commit form but are not yet canonical.

#### `committed`

Durable writes have succeeded.
The object state transition is now official.

#### `reported`

The user has been told what changed and what artifacts prove it.

#### `failed`

The command could not complete.

#### `aborted`

The command was intentionally stopped.

### Command Transition Graph

```text
invoked
  -> resolved
  -> validated
  -> executing
  -> staged
  -> committed
  -> reported
```

Alternative exits:

```text
validated -> failed
executing -> failed
executing -> aborted
staged -> failed
committed -> reported
```

### Command Invariants

* No command should report success before commit.
* No command should skip validation.
* Multi-artifact commands must leave the filesystem truthful even on failure.
* Failure must preserve earlier durable artifacts.

---

## Legal Command Rules

Commands should only be legal when their target object is in a compatible state.

### Scintilla Commands

| Command                   | Legal From                               | Transition                       |
| ------------------------- | ---------------------------------------- | -------------------------------- |
| `azq capture`             | `not_captured`                           | creates audio, transcript, spark |
| `azq sparks`              | any                                      | no state change                  |
| `azq spark show <id>`     | `reviewable`, `linked`, `archived`       | no state change                  |
| `azq spark search <text>` | any with sparks                          | no state change                  |
| `azq spark rm <id>`       | `reviewable` or policy-approved `linked` | to archive or prune              |

### Finis Commands

| Command                 | Legal From                         | Transition               |
| ----------------------- | ---------------------------------- | ------------------------ |
| `azq fine`              | reviewable sparks exist            | sparks to proposed goals |
| `azq goal create`       | reviewable sparks or direct intent | to `active`              |
| `azq goal add`          | direct intent                      | to `active`              |
| `azq goals`             | any                                | no state change          |
| `azq goal show <id>`    | any existing goal                  | no state change          |
| `azq goal close <id>`   | `active`                           | to `completed`           |
| `azq goal archive <id>` | `active`, `paused`, `completed`    | to `archived`            |

### Formam Commands

| Command                          | Legal From                 | Transition      |
| -------------------------------- | -------------------------- | --------------- |
| `azq form build <goal_id>`       | `active goal`              | to `drafted`    |
| `azq form map <goal_id>`         | drafted deliverables exist | to `mapped`     |
| `azq form list`                  | any                        | no state change |
| `azq form show <deliverable_id>` | existing deliverable       | no state change |

### Agenda Commands

| Command                       | Legal From                  | Transition       |
| ----------------------------- | --------------------------- | ---------------- |
| `azq dag build <goal_id>`     | approved deliverables exist | to `ready` tasks |
| `azq task list`               | any                         | no state change  |
| `azq task start <task_id>`    | `ready`                     | to `in_progress` |
| `azq task complete <task_id>` | `in_progress`               | to `completed`   |
| `azq task block <task_id>`    | `in_progress`               | to `blocked`     |
| `azq task cancel <task_id>`   | `ready`, `blocked`          | to `canceled`    |

### Domum Commands

| Command                 | Legal From                   | Transition                       |
| ----------------------- | ---------------------------- | -------------------------------- |
| `azq archive`           | any archivable object exists | move selected objects to archive |
| `azq archive goal <id>` | archivable goal exists       | to `archived`                    |
| `azq archive task <id>` | archivable task exists       | to `archived`                    |
| `azq prune`             | stale reviewed objects exist | to `pruned` or archived          |
| `azq review`            | any                          | mark stale objects as reviewed   |
| `azq report health`     | any                          | no state change                  |
| `azq status`            | any                          | no state change                  |
| `azq doctor`            | any                          | no state change                  |

---

## Filesystem Transition Rules

For every object, AZQ should be able to answer three questions:

1. Where does it live while active?
2. What file proves its state?
3. Where does it go when it leaves active circulation?

### Scintilla

| Object        | Active Proof                          | Archive Destination    |
| ------------- | ------------------------------------- | ---------------------- |
| audio capture | `data/scintilla/audio/<id>.wav`       | `data/archive/sparks/` |
| transcript    | `data/scintilla/transcripts/<id>.txt` | `data/archive/sparks/` |
| spark record  | `data/scintilla/sparks/<id>.json`     | `data/archive/sparks/` |

### Finis

| Object | Active Proof                                          | Archive Destination   |
| ------ | ----------------------------------------------------- | --------------------- |
| goal   | `data/finis/goals/FINIS_*.md` or transitional storage | `data/archive/goals/` |
| review | `data/finis/reviews/`                                 | `data/archive/goals/` |

### Formam

| Object      | Active Proof                        | Archive Destination                                |
| ----------- | ----------------------------------- | -------------------------------------------------- |
| deliverable | `data/form/deliverables/DELIV_*.md` | `data/archive/artifacts/` or `data/archive/goals/` |
| map         | `data/form/maps/GOAL_*_MAP.md`      | `data/archive/artifacts/`                          |

### Agenda

| Object   | Active Proof                  | Archive Destination   |
| -------- | ----------------------------- | --------------------- |
| task     | `data/agenda/tasks/TASK_*.md` | `data/archive/tasks/` |
| dag      | `data/agenda/dags/*.json`     | `data/archive/tasks/` |
| work log | `data/agenda/logs/`           | `data/archive/tasks/` |

### Artifacts

| Object            | Active Proof         | Archive Destination       |
| ----------------- | -------------------- | ------------------------- |
| produced artifact | `data/artifacts/...` | `data/archive/artifacts/` |

---

## Cross-Stage Traceability

Every later-stage object should point backward.

### Required Backlinks

* spark -> source transcript and audio or text capture id
* goal -> linked spark ids
* deliverable -> goal id
* task -> deliverable id
* artifact -> task ids and deliverable id
* archive record -> original active path and archive reason

The formal trace chain is:

```text
artifact -> task -> deliverable -> goal -> spark -> transcript -> audio
```

This makes the system reversible and inspectable.

---

## Failure States

AZQ should represent failure explicitly.

### Common Failure States

* `capture_failed`
* `transcription_failed`
* `extraction_failed`
* `goal_rejected`
* `form_rejected`
* `task_blocked`
* `archive_failed`
* `corrupt`

### Failure Policy

* failure must preserve prior durable artifacts
* failure must not fabricate later-stage artifacts
* failure should write logs when appropriate
* corruption must be surfaced, not hidden

Examples:

* if transcription fails, keep the `.wav`
* if extraction fails, keep the transcript
* if goal creation fails, do not write a partial goal
* if archive fails, leave the active artifact untouched

---

## Current Implementation Gaps

The current repository implements only part of the formal lifecycle.

### Implemented Now

* Scintilla capture pipeline
* spark listing, viewing, search, deletion
* Finis proposal and goal management

### Specified But Not Yet Implemented

* Formam deliverables and maps
* Agenda tasks, DAGs, and logs
* Domum archive, prune, review, doctor, status
* first-class artifact verification and publication markers
* repository health classification

This document should be treated as the target state contract for those missing engines.

---

## Recommended Next Implementation Order

1. Normalize Finis storage to match the filesystem model.
2. Introduce Formam deliverable files and map files.
3. Introduce Agenda task files and work logs.
4. Introduce artifact verification markers in `data/artifacts/`.
5. Introduce Domum archiving before adding more destructive deletion.
6. Add `status` and `doctor` as repository-wide state readers.

This order preserves the craft sequence and avoids building execution before form.

---

## Formal Summary

The state model is the brain of AZQ.

Its central contract is:

```text
No command may bypass the craft pipeline.
No meaningful state may exist only in memory.
No later-stage object may exist without a traceable earlier-stage parent.
No deletion should occur silently.
No command may claim completion without durable evidence.
```

That is the brain of the system.

---

## Open Design Question

What state transitions happen when commands run?

This question should remain active during implementation reviews.
Every new command should answer it explicitly before it is accepted.

