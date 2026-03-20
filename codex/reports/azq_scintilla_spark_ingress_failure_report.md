# AZQ Scintilla Spark Ingress Failure Report

## Executive Summary

AZQ currently has exactly one live spark-ingress path in code: `azq capture`, which routes through microphone capture, Whisper transcription, and spark extraction. That path is implemented in `azq/scintilla/cli.py`, `azq/scintilla/capture.py`, `azq/scintilla/transcribe.py`, and `azq/scintilla/extract.py`.

For this workflow, that is not usable because microphone-based capture is off the table. There is no live text-native spark loading command in `azq/cli.py` or `azq/scintilla/cli.py`, and the implementation plan already states that "no text-native capture path exists" today.

The smallest practical fix is to add a text-native Scintilla ingress path that writes a canonical transcript file and canonical spark JSON under `data/scintilla/`, then reuses the existing extraction flow. The narrowest safe command surface is `azq capture text "..."`, because that exact shape already appears in `docs/architecture/AZQ_COMMAND_MODEL.md` and `docs/architecture/AZQ_STATE_MODEL.md`.

## Current Live Spark Ingress

| Area | Live behavior on disk |
| --- | --- |
| Top-level CLI | `azq/cli.py` prints only `capture`, `sparks`, `spark <id>`, `spark rm <id>`, and `spark search <text>` for Scintilla. |
| Scintilla router | `azq/scintilla/cli.py` dispatches only `capture`, `sparks`, `spark <id>`, `spark rm <id>`, and `spark search <text>`. |
| Write path | `capture_loop()` in `azq/scintilla/cli.py` calls `capture.record()`, then `transcribe.run(audio)`, then `extract.run(transcript)`. |
| Capture source | `azq/scintilla/capture.py` uses `sounddevice` input discovery and recording. If no microphone input device exists, it raises `RuntimeError("No microphone input devices found")`. |
| Transcript creation | `azq/scintilla/transcribe.py` loads Whisper and writes `data/scintilla/transcripts/<spark_id>.txt`. |
| Spark creation | `azq/scintilla/extract.py` reads a transcript file, splits on `.`, lowercases the extracted text, and writes `data/scintilla/sparks/<spark_id>.json`. |
| Read surfaces | `azq/scintilla/sparks.py`, `spark_view.py`, `spark_search.py`, and `spark_delete.py` all operate on canonical files under `data/scintilla/`. |

Current checked-in data under `data/scintilla/` also matches that live path: each visible bundle has a `.wav`, `.txt`, and `.json` file with the same stem.

## Failure For This Workflow

The current live ingress fails this workflow for one reason: the only implemented way to create a spark starts with microphone capture.

That failure is grounded in multiple places:

- `azq/scintilla/cli.py` exposes no text-loading or text-capture branch.
- `azq/scintilla/capture.py` is microphone-specific and cannot ingest plain text.
- `README.md` says `azq capture` "starts the interactive audio capture loop".
- `docs/architecture/AZQ_IMPLEMENTATION_PLAN.md` explicitly says "no text-native capture path exists".

That means Scintilla can inspect, search, and delete existing sparks, but it cannot load a new spark in a usable way when microphone capture is unavailable.

Two operational smells directly worsen spark loading:

1. `azq/scintilla/transcribe.py` loads the Whisper model at import time and prints status immediately. Any command path that imports this module pays heavyweight transcription setup even before actual work starts.
2. `capture_loop()` prints options `2 -> stop recording` and `3 -> discard recording`, but only handles `"1"` and `"4"` itself. Stop is handled indirectly inside `capture.record()`, and discard is not implemented there. That makes the live intake path more brittle and confusing than the menu suggests.

## Missing Capability

Plainly: a text-native spark loading path does not exist today.

The repository does contain desired direction for one:

- `docs/architecture/AZQ_COMMAND_MODEL.md` lists `azq capture text "..."` as a future-facing Scintilla command.
- `docs/architecture/AZQ_STATE_MODEL.md` includes the transition `not_captured -> captured_text` triggered by `azq capture text`.
- `docs/architecture/AZQ_ENGINE_SPEC.md` names text entry, clipboard input, and quick notes as future Scintilla inputs.

But none of that is implemented in the live CLI or Scintilla modules.

## Smallest Practical Fix

The narrowest practical repair is:

| Item | Recommendation |
| --- | --- |
| New ingress mode | Add a text-native Scintilla path under the existing `capture` command family. |
| Preferred command | `azq capture text "..."` |
| Why this shape | It already appears in the command model and state model, so it fits repo direction without inventing a new public surface. |
| Write behavior | Create `data/scintilla/transcripts/<spark_id>.txt` from the supplied text, then call the existing extractor to create `data/scintilla/sparks/<spark_id>.json`. |
| Audio behavior | Do not require or synthesize `.wav` output for text ingress. The current read and delete surfaces already tolerate missing bundle members. |
| Extraction behavior | Reuse `azq/scintilla/extract.py` rather than inventing a second spark schema or a second storage format. |

This is smaller and safer than adding a new standalone `spark add`, `spark import`, or redesigning Scintilla storage. It fixes the immediate red-state ingress failure while staying inside the existing capture stage and existing canonical artifact homes.

Likely command-surface options, from most to least aligned:

| Option | Fit |
| --- | --- |
| `azq capture text "..."` | Best fit. Already named in repo docs. Keeps ingress under Scintilla capture. |
| `azq capture text` with prompt/stdin fallback | Also reasonable as a second form of the same command family. |
| `azq spark add "..."` | Possible, but less aligned with current docs and would introduce a new singular-object write verb. |

Conservative judgment: the first option is clearly the safest because it matches both the current architecture prose and the smallest code change shape.

## Likely File Touch Points

Most likely implementation files:

| File | Why it likely changes |
| --- | --- |
| `azq/scintilla/cli.py` | Add parsing and dispatch for `capture text ...`. |
| `azq/cli.py` | Update printed command listing so the live CLI advertises the new path. |
| `azq/scintilla/storage.py` | Possibly no change, but this is the natural seam if a helper for allocating a new spark id or transcript-first bundle writing is added. |
| `azq/scintilla/extract.py` | Likely reused unchanged; only worth touching if encoding or explicit text-source handling is needed. |
| `tests/test_stage3_wave_d.py` | Add regression coverage for text-native ingress and the resulting canonical artifacts. |

Possible but avoid-if-possible touch points:

- `azq/scintilla/transcribe.py`: should stay untouched for the minimal fix, because text ingress should bypass Whisper entirely.
- `azq/scintilla/capture.py`: should stay microphone-specific for the minimal fix.

## Minimum Test Surface

Minimum proof should stay narrow:

| Test | Why it is enough |
| --- | --- |
| CLI command creates transcript and spark JSON from text input | Proves a human can load a spark without microphone capture. |
| `azq sparks` lists the new spark | Proves the new artifact lands in the existing read surface. |
| `azq spark <id>` shows the transcript text and extracted sparks for the new bundle | Proves exact-id inspection still works for text-ingested sparks. |
| No audio artifact is required for the text path | Proves the fix does not depend on microphone or fake `.wav` output. |

The existing Stage 3 Wave D tests already cover listing, exact-id read, search, and delete against canonical Scintilla storage. The new tests only need to prove that text ingress can create a bundle those existing surfaces can consume.

## Recommended Next Step

Implement `azq capture text "..."` as a transcript-first path that writes `data/scintilla/transcripts/<spark_id>.txt`, reuses `extract.run(...)` to write `data/scintilla/sparks/<spark_id>.json`, and leaves audio absent for that ingress mode.

That is the narrowest safe implementation because it:

- fixes the real workflow blocker immediately
- matches documented future command direction already present in the repo
- reuses current storage and extraction behavior
- avoids Whisper, microphone, and broader Scintilla redesign

## Closing Summary

Live Scintilla ingress is currently audio-only. That is why AZQ cannot load a spark in a usable way for this workflow.

Text-native spark loading does not exist today in code. The smallest practical repair is to add `azq capture text "..."` and have it create the same canonical Scintilla artifacts the rest of the system already knows how to read: a transcript file plus a spark JSON file under `data/scintilla/`.

Approximate judgment: the only meaningful implementation choice is whether the text command also supports prompt/stdin input. The core repair itself is not ambiguous.
