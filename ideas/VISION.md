# 🌌 Vision for azq

azq is more than a CLI to ask ChatGPT — it’s an **experiment in amplifying human creativity through the terminal.**

We believe the terminal is not just a place to run commands, but a place to *think with machines*. azq aims to make that experience richer, smarter, and more rewarding.  
Below are the guiding ideas that shape our direction.

---

## ✨ Core Mission
- Provide a **fast, text-first interface** to powerful AI models.
- Capture **context from the repo and git history** so questions are always grounded in the real project state.
- Build an **ever-growing knowledge base** (logs, docs, manpages, diffs) that evolves alongside the codebase.
- Create tools that **teach as they go**, turning every session into a mini-lesson or a seed for future training.

---

## 🚀 Big Ideas

### 1. Repo-Aware Conversations
- Every `azq ask` should include:
  - The current **git commit hash** (project state).
  - Optionally, the **git diff** from the last commit.
  - Key files (README, requirements, recent changes).
- This anchors questions/answers in time, and allows for reproducibility.

### 2. Context Snapshots
- Automatically gather:
  - File tree
  - README + requirements
  - Relevant code snippets
- Ship this alongside the question so the AI can “see” what the repo looks like *right now*.

### 3. Doc Mode
- Integrate **manpages** and **Python docstrings** directly into the workflow.
- Build a repo-wide documentation archive:
  - Concise index of functions/commands used.
  - Full-text manpages stored in `logs/docs/`.
- Goal: richer answers today, training material for better models tomorrow.

### 4. Teaching Mode
- Scrape the repo for all its moving parts (files, imports, tools, styles).
- Auto-generate:
  - A **book-style walkthrough** (Hello World → Finished Project).
  - Scripts for **narrated video lessons**.
- Lean into creativity (talking origami dinosaur narrator, Attila the Hun Python crash course, etc.).

### 5. Ghost Completion
- Experiment with **“paragraph-level completions”** like Copilot, but lightweight:
  - First in terminal (fzf-like preview).
  - Later in VS Code integration.
- Dream: combine azq context-awareness with Copilot’s fluid typing assistance.

### 6. Rewarding CLI Experience
- The terminal is sacred. GUI is for mortals.  
- azq should reward power users with:
  - Clever badges/titles (*azq adept*, *wizard of pipes*).
  - Easter eggs in responses.
  - Logging that feels like a story of progress.

---

## 🌱 Why This Matters
- Every repo becomes not just a project, but a **living dataset**.
- Every question/answer pair is **anchored in history**.
- azq could eventually help train **better domain-specific models** by providing a stream of:
  - Context (git state, diffs, docs).
  - Dialogue (questions + answers).
  - Reflections (ideas folder, vision notes).

---

## 🛠 Next Steps
- Stabilize `ask`, `doc`, and `import` commands.
- Add `git log` + `git diff` integration.
- Experiment with “context snapshot” files on each question.
- Continue capturing ideas in `ideas/` — no thought too wild.

---

*azq is the command line whisperer. May it grow weird and wonderful.*

