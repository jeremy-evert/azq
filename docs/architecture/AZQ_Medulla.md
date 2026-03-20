# AZQ Medulla

## Purpose

This document is the pith at the heart of AZQ.

It exists so that every other architecture document, implementation plan, prompt, report, command surface, storage rule, and future build artifact can be checked against one small governing standard.

If a larger document becomes cloudy, this document should remain clear.

If multiple documents disagree, this document should help reveal which one has wandered.

---

## Core Sentence

**AZQ exists to preserve human intent, lineage, and continuity while shaping LLM-assisted work from spark to action.**

---

## Core Standard

**Any feature, document, command, artifact, or automation that weakens human intent, obscures lineage, or breaks continuity is not AZQ-compliant.**

---

## What This Means

### 1. Preserve human intent

AZQ must help the human keep hold of what they meant before, during, and after interaction with an LLM.

The system must not silently let model output replace human purpose.

### 2. Preserve lineage

AZQ must make it possible to trace where something came from.

A spark should be traceable to a goal.
A goal should be traceable to a deliverable.
A deliverable should be traceable to a task.
A task should be traceable to later execution and stewardship artifacts.

If something cannot be traced, AZQ is losing its shape.

### 3. Preserve continuity

AZQ must help work remain inspectable, resumable, and understandable across time.

The human should be able to return later and still understand:

- what was captured
- what was accepted
- what was proposed
- what changed
- what remains
- what happened next

If the system causes work to dissolve into disconnected transcripts, forgotten edits, or silent deletion, it is failing continuity.

### 4. Shape LLM-assisted work

AZQ is not merely a passive notebook.

It should help shape work through its craft sequence without surrendering authorship to the model.

The model may assist.
The model may propose.
The model may help clarify, decompose, or package work.

But AZQ must keep visible the difference between:

- human-origin intent
- model-origin suggestion
- accepted canonical state

### 5. Move from spark to action

AZQ should help the human move from fleeting thought to durable work.

That movement should be structured, inspectable, and file-backed.

The living craft path is:

```text
spark -> goal -> deliverable -> task -> action -> stewardship
````

This path is not merely a pipeline.
It is the continuity spine of the system.

---

## Operational Questions

When evaluating a document, command, artifact, or proposed feature, ask:

1. Does this preserve or distort human intent?
2. Does this clarify or obscure lineage?
3. Does this strengthen or weaken continuity?
4. Does this help shape LLM-assisted work without hiding what the model contributed?
5. Does this serve the path from spark to action?

If the answer is no to these questions, the work should be revised before it is treated as canonical.

---

## Authority

This document is intentionally small.

It does not replace the implementation plan, engine spec, command model, filesystem model, state model, or charter.

It exists to govern them.

Those documents may provide detail.
This document provides the standard.

When a larger document becomes confusing, overgrown, or contradictory, AZQ Medulla should be used as the first clarity check.

---

## Non-Negotiables

The following are always out of bounds for AZQ:

* silent replacement of human intent with model language
* hidden loss of lineage
* destructive state changes that erase continuity without stewardship
* command or storage behavior that makes accepted state indistinguishable from proposal state
* architecture drift that turns AZQ into a generic task manager or a loose pile of helper scripts

---

## Closing

AZQ is a human-first wrapper for LLM-assisted work.

Its job is not to impress.
Its job is to preserve the mind of the worker while the work is being shaped.

That is the marrow.

Preserve intent.
Preserve lineage.
Preserve continuity.
Shape the work.
Move from spark to action.
