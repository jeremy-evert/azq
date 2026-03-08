Excellent moment to do this, Jeremy. The **README is the keystone**. If the README is clear, the repository feels alive from day one. If it's muddy, the project feels like a junk drawer.

Let’s write a README that does four things:

1. Explains **what AZQ is**
2. Explains the **Rule of Craft**
3. Explains **Scintilla**
4. Shows **how to run the first engine**

Clean. Clear. No bloat.

You can drop this directly into `README.md`.

---

# README.md

```markdown
# AZQ

AZQ is a system for turning human thought into durable work.

It is built around a simple rule of craft: ideas must be gathered,
shaped, and acted upon in a deliberate sequence.

The system is divided into a small number of engines. Each engine
represents a different stage in the craft process.

---

## The Rule of Craft

The AZQ system follows five stages:

| Rule | Meaning |
|-----|------|
| **Cole Scintilla** | Gather sparks (ideas) |
| **Fine Finem** | Define purpose |
| **Strue Formam** | Build structure |
| **Age Agenda** | Execute work |
| **Custodi Domum** | Maintain the system |

Each stage is implemented as a small engine inside the AZQ repository.

The engines are designed to be simple, composable tools rather than
large monolithic systems.

---

## First Engine: Cole Scintilla

The first engine captures ideas.

Ideas are fragile. They appear while driving, teaching, debugging,
or walking. If they are not captured immediately, they vanish.

The purpose of **Cole Scintilla** is to gather those sparks and store
them permanently.

The engine performs three actions:

1. Record a thought
2. Transcribe the audio
3. Extract atomic ideas ("sparks")

Pipeline:

```

audio → transcript → sparks

```

Example output:

```

scintilla/audio/2026-03-08_1812.wav
scintilla/transcripts/2026-03-08_1812.txt
scintilla/sparks/2026-03-08_1812.json

````

Example sparks file:

```json
[
  {
    "spark": "create latin grammar for project tools",
    "confidence": 0.91
  },
  {
    "spark": "build spark capture system first",
    "confidence": 0.88
  }
]
````

---

## Repository Structure

```
azq/

azq/
    scintilla/
        capture.py
        transcribe.py
        extract.py

data/
    scintilla/
        audio/
        transcripts/
        sparks/
```

Code lives in `azq/`.

Captured ideas live in `data/`.

---

## Philosophy

The system deliberately refuses to do too much too early.

Scintilla does **not**:

* plan projects
* summarize work
* generate tasks
* build dependency graphs
* execute code

Those responsibilities belong to later engines.

Scintilla has only one purpose:

**Gather sparks.**

---

## Status

The project is in early development.

Current focus:

Implement the **Cole Scintilla** engine.

Future engines will expand the craft rule.

---

