from datetime import date

from azq.finis.storage import load_goal, next_goal_id, write_goal


def add_goal():
    print("Enter goal title:")
    title = input("> ").strip()
    if not title:
        print("Goal cannot be empty.")
        return

    print("Enter goal description (optional):")
    description = input("> ").strip()

    goal_id = next_goal_id()
    goal_record = {
        "goal_id": goal_id,
        "title": title,
        "status": "active",
        "created": str(date.today()),
        "description": description,
        "derived_from": [],
    }
    write_goal(goal_record)
    print(f"Goal created → {goal_id}")


def close_goal(goal_id):
    goal_record = load_goal(goal_id)
    if goal_record is None:
        print("Goal not found.")
        return

    goal_record["status"] = "completed"
    write_goal(goal_record)
    print(f"Goal {goal_id} marked completed")


def archive_goal(goal_id):
    goal_record = load_goal(goal_id)
    if goal_record is None:
        print("Goal not found.")
        return

    goal_record["status"] = "archived"
    write_goal(goal_record)
    print(f"Goal {goal_id} archived")
