# AZQ Bootstrap

## Purpose

This document defines the shortest reliable path from an empty repository to a living AZQ instance.

In AZQ terms, a repository is **living** when:

1. the package installs and the `azq` command runs
2. at least one spark has been captured
3. at least one goal exists
4. the filesystem contains durable evidence of the flow

The bootstrap is intentionally minimal.
It is not a full setup guide for every future engine.
It is the first proof that the craft loop is alive.

---

## What Bootstrap Means Right Now

Given the current codebase, bootstrap does **not** mean that all five engines are implemented.

It means the repository has successfully completed the first live loop:

```text
capture -> spark -> goal
```

That corresponds to the currently implemented subset of AZQ:

* **Cole Scintilla** is operational
* **Respice Finem** is operational in its current form
* **Strue Formam**, **Age Agenda**, and **Custodi Domum** remain mostly specified but not yet fully implemented fileciteturn8file3turn8file7

So the goal of bootstrap is modest and precise:

> prove that AZQ can gather one spark and turn it into one goal.

---

## Target State

By the end of bootstrap, the repository should contain visible craft artifacts such as:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
data/finis/goals.json
```

That moves the repository from `empty` to at least `purposed` in the current state model. fileciteturn8file7

---

## Preconditions

Before starting, you should have:

* Python 3 available
* a working virtual environment tool (`venv`)
* a working microphone if you plan to use voice capture
* the repository checked out locally

If audio capture is unavailable, AZQ can still be installed, but it is not yet a living Scintilla instance under the current implementation.

---

## 1. Start At Repository Root

If starting from nothing:

```bash
mkdir azq
cd azq
git init
```

If the repository already exists, start at its root.

Sanity check:

```bash
pwd
ls
```

You should be standing where `pyproject.toml` lives.

---

## 2. Create A Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

This keeps the bootstrap isolated and reproducible.

---

## 3. Install AZQ In Editable Mode

```bash
python -m pip install -e .
```

This should create the `azq` command from the package entry point.

Quick proof:

```bash
azq
```

Expected result:

* the CLI runs
* available commands are printed

At this point, the repository is **installed** but not yet living.

---

## 4. Create Required Directories

Some directories may already exist in the repo. If not, create them.

```bash
mkdir -p \
  data/scintilla/audio \
  data/scintilla/transcripts \
  data/scintilla/sparks \
  data/finis \
  logs \
  scripts \
  tests
```

This step keeps the filesystem aligned with the current working subset while remaining compatible with the broader filesystem model. fileciteturn8file4

Quick proof:

```bash
find data -maxdepth 3 -type d | sort
```

---

## 5. Confirm Cole Scintilla Works

AZQ begins with **Cole Scintilla**.

The first working loop is:

```text
audio -> transcript -> sparks
```

Run:

```bash
azq capture
```

Inside the capture loop, use the current implemented controls shown by the CLI.
In the current repository, the live path is effectively:

1. start recording
2. speak one short idea aloud
3. stop recording
4. allow transcription and extraction to finish
5. exit capture mode

If successful, AZQ should create files like:

```text
data/scintilla/audio/YYYY-MM-DD_HHMMSS.wav
data/scintilla/transcripts/YYYY-MM-DD_HHMMSS.txt
data/scintilla/sparks/YYYY-MM-DD_HHMMSS.json
```

Notes:

* a working microphone is required
* the first Whisper run may take longer because the model must load locally
* if transcription fails, the audio file should still remain as durable evidence of capture according to the state model fileciteturn8file7

At this point, the repository should be at least `seeded`. fileciteturn8file7

---

## 6. Verify The Spark Layer

List all sparks:

```bash
azq sparks
```

Inspect a specific spark using the currently implemented syntax:

```bash
azq spark <spark_id>
```

Search sparks:

```bash
azq spark search "<text>"
```

What you are proving here:

* capture created durable artifacts
* spark records are visible
* sparks are searchable
* the filesystem is telling the truth

---

## 7. Create The First Goal

Now promote sparks into purpose.

### Interactive path

```bash
azq fine
```

This uses the current Finis workflow to surface or derive candidate goals from spark files.

### Direct path

```bash
azq goal add
```

Then type one clear goal statement.

If successful, the current implementation writes:

```text
data/finis/goals.json
```

List active goals:

```bash
azq goals
```

At this point, the repository is `purposed` in the current state model. fileciteturn8file7

---

## 8. Proof Of Life

Bootstrap is complete when these commands all work:

```bash
azq
azq sparks
azq goals
```

And these visible artifacts exist on disk:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
data/finis/goals.json
```

That is the first living AZQ instance.

It proves:

* capture exists
* memory exists
* purpose exists
* the filesystem proves it

---

## 9. Smallest Acceptable Bootstrap

If you want the shortest acceptable sequence, it is this:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
mkdir -p data/scintilla/audio data/scintilla/transcripts data/scintilla/sparks data/finis
azq capture
azq sparks
azq fine
azq goals
```

Nothing more is required for the first live loop.

---

## 10. What Not To Add Yet

Do **not** add these during bootstrap:

* task systems
* databases
* web UIs
* background daemons
* orchestration layers
* multi-engine automation
* new storage layers that hide the visible artifacts

Bootstrap is finished when AZQ can gather one spark and turn it into one goal.

That is enough to prove the system is alive.

---

## 11. Common Failure Cases

### `azq` command does not run

Check:

```bash
python -m pip install -e .
which azq
```

### Audio capture fails

Check:

* microphone availability
* host audio permissions
* whether the machine supports the current capture stack

### Transcription fails

Check:

* local model availability
* Python package dependencies
* whether audio was still written to `data/scintilla/audio/`

### Goal creation fails

Check:

* whether spark files exist in `data/scintilla/sparks/`
* whether `data/finis/` exists and is writable

Bootstrap should fail loudly rather than pretending success.

---

## 12. After Bootstrap

Once bootstrap succeeds, the next sensible steps are:

1. normalize Finis storage toward file-based goals
2. implement Formam deliverables and maps
3. implement Agenda tasks and logs
4. implement Domum archive, prune, and health reporting

But those are **post-bootstrap** concerns.

Bootstrap ends with living capture and living purpose.

---

## Closing

Bootstrap is not the whole system.
It is the first pulse.

If AZQ can gather one spark, preserve it, and elevate it into one real goal, then the repository has crossed the line from static code to living craft.

That is enough for day one.

