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

## Live Baseline

The current repository has the first two live craft loops implemented:

```text
capture -> spark -> goal -> deliverable -> map
```

That means:

* **Cole Scintilla** is live for capture and spark storage
* **Respice Finem** is live for goal creation and listing
* **Strue Formam** is live for canonical deliverable and goal-map storage
* **Age Agenda** and **Custodi Domum** remain later architectural stages rather than active operators

The active Stage 1 and Stage 2 storage model is file-backed.
Canonical Finis goals live as one file per goal under `data/finis/goals/`.
`data/finis/goals.json` is legacy migration input only and should not be treated as the active system of record.
Canonical Formam deliverables live as one file per deliverable under `data/form/deliverables/`.
Canonical Formam goal maps live as one file per goal under `data/form/maps/`.

---

## Canonical Storage

The visible source of truth lives in the repository tree:

```text
data/scintilla/audio/
data/scintilla/transcripts/
data/scintilla/sparks/
data/finis/goals/
data/form/deliverables/
data/form/maps/
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

Formam adds canonical Stage 2 records such as:

```text
data/form/deliverables/DELIV_001.md
data/form/maps/GOAL_FINIS_001_MAP.md
```

`data/form/deliverables/` and `data/form/maps/` are the canonical Stage 2 system of record.
Operators should inspect those files directly when they need to verify the live deliverable set or the current goal-level dependency map.

---

## Repository Structure

```text
azq/
  azq/
    scintilla/
    finis/
    formam/
    cli.py
  data/
    scintilla/
      audio/
      transcripts/
      sparks/
    finis/
      goals/
    form/
      deliverables/
      maps/
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
azq form build <goal_id>
azq form list
azq form show <deliverable_id>
azq form map <goal_id>
```

After creating a goal, the durable proof should be a goal file in `data/finis/goals/`, not a write to `data/finis/goals.json`.
After building form, the durable proof should be a deliverable file in `data/form/deliverables/` and a goal map in `data/form/maps/`.

---

## Status

AZQ is in early development.
Stage 1 normalized Finis storage so later engines could depend on canonical file-backed goals without transitional glue.
Stage 2 now uses canonical file-backed Formam records as the live baseline for deliverables and goal maps.
