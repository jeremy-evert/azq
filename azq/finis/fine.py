import json
import difflib
from pathlib import Path
from .goals import load_goals, save_goals, next_goal_id

SPARK_DIR = Path("data/scintilla/sparks")


def load_sparks():
    """Read all spark files."""
    sparks = []

    for file in sorted(SPARK_DIR.glob("*.json")):
        with open(file) as f:
            data = json.load(f)

        for s in data:
            sparks.append({
                "spark": s["spark"],
                "source": file.name
            })

    return sparks

def similar(a, b):
    """Return similarity ratio between two strings."""
    return difflib.SequenceMatcher(None, a, b).ratio()

def propose_goals(sparks):
    """Convert sparks into candidate goals."""

    existing_goals = load_goals()

    existing_text = [
        g["goal"].lower()
        for g in existing_goals
    ]

    candidates = []

    for s in sparks:

        text = s["spark"].strip()

        if len(text) < 10:
            continue

        text_lower = text.lower()

        duplicate = False

        for g in existing_text:

            if similar(text_lower, g) > 0.75:
                duplicate = True
                break

        if duplicate:
            continue

        candidates.append({
            "goal": text.capitalize(),
            "source": s["source"]
        })

    return candidates


def confirm_goals(candidates):
    """Ask user which goals to keep."""
    confirmed = []

    print("\nCandidate Goals\n")

    for i, c in enumerate(candidates):

        print(f"{i+1}. {c['goal']}")

        ans = input("Accept goal? [y/n] ")

        if ans.lower().startswith("y"):
            confirmed.append(c)

    return confirmed


def run_fine():
    """Main Fine Finem engine."""

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
            "derived_from": [c["source"]]
        })

    save_goals(goals)

    print("\nGoals written to data/finis/goals.json")
