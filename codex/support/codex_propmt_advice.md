# What a Good Codex Prompt Looks Like

Here is the pattern you seem to be discovering:

> A good Codex prompt is not just "write me X."
>
> It is closer to a compact engineering brief.

## 1. Say Exactly What File to Produce

Be concrete.

Include:

- the exact filename
- the exact output type
- whether the result should be a drop-in replacement or a new file

## 2. Tell It to Inspect the Repo First

This matters a lot.

Useful instructions include:

- inspect the repository before drafting
- read the current manifest and checks files first
- validate against live filenames and the current module layout
- do not assume the docs are perfectly current

## 3. State the Purpose of the Artifact

Do not just say "make checks."

Say what kind of artifact this is and what it is trying to protect.

Examples:

- this is a refactor-prep wave
- this is a closeout wave
- this should preserve behavior
- this should prevent scope creep

That gives it doctrine instead of vibes.

## 4. Separate Hard Constraints from Preferences

This helps a lot.

### Required

- valid JSON
- match the current runner format
- include all Wave D tasks
- use baseline checks plus task-specific checks

### Preferred

- use behavior checks over grep checks
- keep brittle architecture policing in `human_checks`
- avoid exact implementation assumptions unless required

## 5. Be Explicit About What It Must Not Do

This is one of the highest-value parts.

For Codex, "do not" is gold.

Examples:

- do not invent files not grounded in the repo
- do not assume refactors already happened
- do not broaden into Stage 3 behavior
- do not silently edit the task manifest unless asked
- do not use fragile text checks when behavior checks are possible

## 6. Ask It to Explain Reality Mismatches

This is huge.

If something is weird, tell Codex to say so plainly.

Examples:

- if the manifest and the repo disagree, say so
- if a check is underspecified, note it
- if a hard check would be brittle, move it to `human_checks` and explain why

---

That is how you turn it from a code vending machine into a junior engineer with a pulse.
