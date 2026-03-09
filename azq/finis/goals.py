import json
from pathlib import Path

GOALS_PATH = Path("data/finis/goals.json")


def load_goals():
    if not GOALS_PATH.exists():
        return []

    with open(GOALS_PATH, "r") as f:
        return json.load(f)


def save_goals(goals):
    GOALS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(GOALS_PATH, "w") as f:
        json.dump(goals, f, indent=2)


def next_goal_id(goals):
    if not goals:
        return "FINIS_001"

    numbers = [
        int(g["goal_id"].split("_")[1])
        for g in goals
    ]

    return f"FINIS_{max(numbers)+1:03d}"
