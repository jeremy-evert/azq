# What a good Codex prompt looks like

Here is the pattern I think you are discovering:

A good Codex prompt is not just “write me X.”

It is more like:

## 1. Tell it what file to produce

Be concrete.

exact filename

exact output type

whether this is a drop-in replacement or a new file

## 2. Tell it to inspect the repo first

This matters a lot.

Say things like:

inspect the repository before drafting

read the current manifest/checks files first

validate against live filenames and current module layout

do not assume the docs are perfectly current

## 3. Tell it the purpose of the artifact

Not just “make checks.”

Tell it:

this is a refactor-prep wave

this is a closeout wave

this should preserve behavior

this should prevent scope creep

That gives it doctrine instead of vibes.

## 4. Separate hard constraints from preferences

This helps a ton.

Example:

Required

valid JSON

match current runner format

include all Wave D tasks

use baseline checks plus task-specific checks

Preferred

use behavior checks over grep checks

keep brittle architecture policing in human_checks

avoid exact implementation assumptions unless required

## 5. Tell it what not to do

This is one of the highest-value parts.

For Codex, “do not” is gold.

Examples:

do not invent files not grounded in the repo

do not assume refactors already happened

do not broaden into Stage 3 behavior

do not silently edit the task manifest unless asked

do not use fragile text checks when behavior checks are possible

## 6. Ask it to explain reality mismatches

This is huge.

If something is weird, tell Codex:

if the manifest and the repo disagree, say so
* if a check is underspecified, note it
* if a hard check would be brittle, move it to human_checks and explain why

---

That turns it from a code vending machine into a junior engineer with a pulse.
