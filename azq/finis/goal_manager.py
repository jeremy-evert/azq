import json
from pathlib import Path
from datetime import date

GOALS_FILE = Path("data/finis/goals.json")


def load_goals():

    if not GOALS_FILE.exists():
        return []

    with open(GOALS_FILE) as f:
        return json.load(f)


def save_goals(goals):

    GOALS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)


def next_goal_id(goals):

    if not goals:
        return "FINIS_001"

    nums = [
        int(g["goal_id"].split("_")[1])
        for g in goals
    ]

    return f"FINIS_{max(nums)+1:03d}"


def add_goal():

    goals = load_goals()

    print("Enter goal:")
    goal_text = input("> ").strip()

    if not goal_text:
        print("Goal cannot be empty.")
        return

    gid = next_goal_id(goals)

    new_goal = {
        "goal_id": gid,
        "goal": goal_text,
        "status": "active",
        "created": str(date.today()),
        "derived_from": []
    }

    goals.append(new_goal)

    save_goals(goals)

    print(f"Goal created → {gid}")


def close_goal(goal_id):

    goals = load_goals()

    for g in goals:

        if g["goal_id"] == goal_id:

            g["status"] = "completed"
            save_goals(goals)

            print(f"Goal {goal_id} marked completed")
            return

    print("Goal not found.")


def archive_goal(goal_id):

    goals = load_goals()

    for g in goals:

        if g["goal_id"] == goal_id:

            g["status"] = "archived"
            save_goals(goals)

            print(f"Goal {goal_id} archived")
            return

    print("Goal not found.")
