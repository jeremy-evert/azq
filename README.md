# AZQ

AZQ is a system for turning human thought into durable work.

It is built around a simple rule of craft: ideas are gathered, given purpose, shaped into structure, turned into work, and kept with visible evidence on disk.

The repository is organized as a small set of engines, each responsible for one stage in that craft pipeline.

---

## The Rule of Craft

AZQ follows five stages:

| Rule | Meaning |
| ---- | ------- |
| **Cole Scintilla** | Gather sparks |
| **Respice Finem** | Define goals |
| **Strue Formam** | Build deliverables and maps |
| **Age Agenda** | Execute work |
| **Custodi Domum** | Maintain and archive the system |

The filesystem is intended to teach this architecture directly:

```text
spark -> goal -> deliverable -> task -> artifact -> archive
```

---

## Stage 1 Reality

The current repository has the first live loop implemented:

```text
capture -> spark -> goal
```

That means:

* **Cole Scintilla** is live for capture and spark storage
* **Respice Finem** is live for goal creation and listing
* later engines remain architectural targets rather than finished code

The active Stage 1 storage model is file-backed.
Canonical Finis goals live as one file per goal under `data/finis/goals/`.
`data/finis/goals.json` is legacy migration input only and should not be treated as the active system of record.

---

## Canonical Storage

Stage 1 keeps the visible source of truth in the repository tree:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
data/finis/goals/
```

Finis goal files are human-readable Markdown records such as:

```text
data/finis/goals/FINIS_001.md
data/finis/goals/FINIS_002.md
```

Each canonical goal record exposes the Stage 1 fields:

* `goal_id`
* `title`
* `status`
* `created`
* `description`
* `derived_from`

Where older data used a `goal` field, Stage 1 normalizes that into the canonical `title`.

---

## Repository Structure

```text
azq/
  azq/
    scintilla/
    finis/
    cli.py
  data/
    scintilla/
      audio/
      transcripts/
      sparks/
    finis/
      goals/
```

Code lives in `azq/`.
Visible craft artifacts live in `data/`.

---

## Basic Use

Install in editable mode:

```bash
python -m pip install -e .
```

Run the current live commands:

```bash
azq capture
azq sparks
azq fine
azq goal add
azq goals
```

After creating a goal, the durable proof should be a goal file in `data/finis/goals/`, not a write to `data/finis/goals.json`.

---

## Status

AZQ is in early development.
Stage 1 is focused on normalizing Finis storage so later engines can depend on canonical file-backed goals without transitional glue.
