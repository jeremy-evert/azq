import json
from pathlib import Path

GOALS_FILE = Path("data/finis/goals.json")


def load_goals():
    """Load goals from disk."""
    if not GOALS_FILE.exists():
        return []

    with open(GOALS_FILE) as f:
        return json.load(f)


def save_goals(goals):
    """Write goals to disk."""
    GOALS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)


def next_goal_id(goals):
    """Generate the next FINIS id."""
    if not goals:
        return "FINIS_001"

    nums = [
        int(g["goal_id"].split("_")[1])
        for g in goals
    ]

    return f"FINIS_{max(nums)+1:03d}"


def show_goals():
    """Display current goals."""
    goals = load_goals()

    if not goals:
        print("No goals defined.")
        return

    print("\nActive Goals\n")

    for g in goals:
        print(f"{g['goal_id']}  {g['goal']}  [{g['status']}]")
