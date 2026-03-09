import json
import difflib
from pathlib import Path
from datetime import date

from .goals import load_goals, save_goals, next_goal_id

SPARK_DIR = Path("data/scintilla/sparks")


# ------------------------------------------------
# Load sparks
# ------------------------------------------------

def load_sparks():
    """Read all spark files."""

    sparks = []

    for file in sorted(SPARK_DIR.glob("*.json")):

        with open(file) as f:
            data = json.load(f)

        for s in data:

            sparks.append({
                "spark": s["spark"],
                "source": file.stem
            })

    return sparks


# ------------------------------------------------
# Similarity check
# ------------------------------------------------

def similar(a, b):
    """Return similarity ratio between two strings."""
    return difflib.SequenceMatcher(None, a, b).ratio()


# ------------------------------------------------
# Goal text cleanup
# ------------------------------------------------

def clean_goal_text(text):
    """
    Convert spoken phrases into better goal statements.
    """

    text = text.strip()

    prefixes = [
        "i would like to",
        "i want to",
        "my goal is to",
        "one of the goals that i have is",
        "one goal is to",
        "the goal is to"
    ]

    lower = text.lower()

    for p in prefixes:
        if lower.startswith(p):
            text = text[len(p):].strip()

    # normalize whitespace
    text = " ".join(text.split())

    # capitalize nicely
    text = text[0].upper() + text[1:]

    return text


# ------------------------------------------------
# Extract used spark sources
# ------------------------------------------------

def get_used_sources(goals):

    used = set()

    for g in goals:
        for s in g.get("derived_from", []):
            used.add(s)

    return used


# ------------------------------------------------
# Propose goals
# ------------------------------------------------

def propose_goals(sparks):

    existing_goals = load_goals()

    existing_text = [
        g["goal"].lower()
        for g in existing_goals
    ]

    used_sources = get_used_sources(existing_goals)

    candidates = []

    for s in sparks:

        source = s["source"]

        # skip sparks already used
        if source in used_sources:
            continue

        text = s["spark"].strip()

        if len(text) < 10:
            continue

        text = clean_goal_text(text)

        text_lower = text.lower()

        duplicate = False

        for g in existing_text:

            if similar(text_lower, g) > 0.75:
                duplicate = True
                break

        if duplicate:
            continue

        candidates.append({
            "goal": text,
            "source": source
        })

    return candidates


# ------------------------------------------------
# Confirm goals interactively
# ------------------------------------------------

def confirm_goals(candidates):

    confirmed = []

    if not candidates:
        return confirmed

    print("\nCandidate Goals\n")

    for i, c in enumerate(candidates):

        print(f"{i+1}. {c['goal']}")

        ans = input("Accept goal? [y/n] ")

        if ans.lower().startswith("y"):
            confirmed.append(c)

        print()

    return confirmed


# ------------------------------------------------
# Main Finis engine
# ------------------------------------------------

def run_fine():

    sparks = load_sparks()

    if not sparks:
        print("No sparks found.")
        return

    candidates = propose_goals(sparks)

    confirmed = confirm_goals(candidates)

    if not confirmed:
        print("No goals confirmed.")
        return

    goals = load_goals()

    for c in confirmed:

        goal_id = next_goal_id(goals)

        goals.append({
            "goal_id": goal_id,
            "goal": c["goal"],
            "status": "active",
            "created": str(date.today()),
            "derived_from": [c["source"]]
        })

    save_goals(goals)

    print("\nGoals written to data/finis/goals.json")
