from azq.finis.storage import load_all_goals


def show_goals():
    """Display active goals."""
    goals = load_all_goals()

    if not goals:
        print("No goals defined.")
        return

    active = [g for g in goals if g["status"] == "active"]

    if not active:
        print("No active goals.")
        return

    print("\nActive Goals\n")

    for g in active:
        print(f"{g['goal_id']}  {g['title']}  [{g['status']}]")
