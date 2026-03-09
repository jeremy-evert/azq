import json
from pathlib import Path

GOALS_FILE = Path("data/finis/goals.json")


def load_goals():

    if not GOALS_FILE.exists():
        return []

    with open(GOALS_FILE) as f:
        return json.load(f)


def show_goals():

    goals = load_goals()

    if not goals:
        print("No goals defined.")
        return

    active = [g for g in goals if g["status"] == "active"]

    if not active:
        print("No active goals.")
        return

    print("\nActive Goals\n")

    for g in active:
        print(f"{g['goal_id']}  {g['goal']}  [{g['status']}]")
